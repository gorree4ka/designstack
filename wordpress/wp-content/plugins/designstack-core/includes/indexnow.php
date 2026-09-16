<?php
/**
 * IndexNow: сообщаем поиску об изменении страницы в момент публикации.
 *
 * Карта сайта и обход по счётчику Метрики говорят роботу, что смотреть, но он
 * приходит сам и по своему расписанию. IndexNow — обратное направление: запрос
 * уходит сразу, как только запись опубликовали или переписали.
 *
 * Ключ не секрет по устройству протокола: он лежит в открытом файле в корне
 * сайта, и поиск сверяет с ним каждый запрос. Файл отдаёт не диск, а правило
 * перезаписи с ключом внутри — иначе его пришлось бы класть на хостинг руками
 * и терять при каждой заливке темы.
 *
 * Запросы уходят только с продакшена: локальная правка не должна дёргать поиск.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

const DESIGNSTACK_INDEXNOW_ENDPOINT = 'https://yandex.com/indexnow';
const DESIGNSTACK_INDEXNOW_OPTION   = 'designstack_indexnow_key';
const DESIGNSTACK_INDEXNOW_LOG      = 'designstack_indexnow_last';

/**
 * Ключ IndexNow. Заводится один раз и дальше не меняется: смена ключа
 * обнуляет доверие поиска к сайту, пока он не перечитает новый файл.
 *
 * @param bool $create Завести ключ, если его ещё нет.
 * @return string Ключ или пустая строка.
 */
function designstack_core_indexnow_key( bool $create = false ): string {
	$key = (string) get_option( DESIGNSTACK_INDEXNOW_OPTION, '' );

	if ( $key || ! $create ) {
		return $key;
	}

	$key = bin2hex( random_bytes( 16 ) );
	update_option( DESIGNSTACK_INDEXNOW_OPTION, $key, false );

	// Правило с ключом внутри регистрируется на `init`, а тогда ключа ещё не было.
	// Поэтому здесь сначала регистрируем его сами, иначе сброс запишет правила без него
	// и файл ключа отдастся только после второго запуска (проверено прогоном 16.09.2026).
	designstack_core_indexnow_rewrite();
	flush_rewrite_rules( false );

	return $key;
}

/**
 * Правило для файла ключа: `/<ключ>.txt`.
 *
 * Ключ вшит в само правило, поэтому чужие адреса вида `/robots.txt` оно не перехватывает.
 *
 * @return void
 */
function designstack_core_indexnow_rewrite(): void {
	$key = designstack_core_indexnow_key();

	if ( ! $key ) {
		return;
	}

	add_rewrite_rule( '^' . preg_quote( $key, '/' ) . '\.txt$', 'index.php?designstack_indexnow=1', 'top' );
}
add_action( 'init', 'designstack_core_indexnow_rewrite' );

/**
 * Свой параметр запроса для файла ключа.
 *
 * @param array<int, string> $vars Параметры.
 * @return array<int, string>
 */
function designstack_core_indexnow_query_var( array $vars ): array {
	$vars[] = 'designstack_indexnow';

	return $vars;
}
add_filter( 'query_vars', 'designstack_core_indexnow_query_var' );

/**
 * Отдаёт файл ключа обычным текстом.
 *
 * @return void
 */
function designstack_core_indexnow_serve(): void {
	if ( ! get_query_var( 'designstack_indexnow' ) ) {
		return;
	}

	$key = designstack_core_indexnow_key();

	if ( ! $key ) {
		return;
	}

	status_header( 200 );
	header( 'Content-Type: text/plain; charset=utf-8' );
	header( 'X-Robots-Tag: noindex' );
	echo esc_html( $key );
	exit;
}
add_action( 'template_redirect', 'designstack_core_indexnow_serve', 0 );

/**
 * Типы записей, об изменении которых стоит сообщать.
 *
 * @return array<int, string>
 */
function designstack_core_indexnow_types(): array {
	return array( 'resource', 'lesson', 'post', 'page' );
}

/**
 * Отправляет адреса в IndexNow.
 *
 * Возвращает ответ по каждому адресу, чтобы результат можно было проверить, а не
 * предположить. Ответ 200 — принято, 202 — принято, ключ ещё проверяется.
 *
 * @param array<int, string> $urls  Полные адреса страниц.
 * @param bool               $force Отправить даже не с продакшена (для ручной проверки).
 * @return array<int, array{url: string, code: int|string}>
 */
function designstack_core_indexnow_submit( array $urls, bool $force = false ): array {
	$urls = array_values( array_unique( array_filter( $urls ) ) );

	if ( ! $urls ) {
		return array();
	}

	if ( ! $force && ! designstack_core_is_production() ) {
		return array( array( 'url' => $urls[0], 'code' => 'не продакшен, запрос не ушёл' ) );
	}

	$key  = designstack_core_indexnow_key( true );
	$host = (string) wp_parse_url( home_url(), PHP_URL_HOST );
	$out  = array();

	foreach ( $urls as $url ) {
		// Чужой адрес поиск отклонит с 422, и правильно: ключ подтверждает только наш домен.
		if ( wp_parse_url( $url, PHP_URL_HOST ) !== $host ) {
			$out[] = array( 'url' => $url, 'code' => 'чужой домен' );
			continue;
		}

		$response = wp_remote_get(
			add_query_arg(
				array(
					'url' => rawurlencode( $url ),
					'key' => $key,
				),
				DESIGNSTACK_INDEXNOW_ENDPOINT
			),
			array(
				'timeout'     => 8,
				'redirection' => 2,
			)
		);

		$code  = is_wp_error( $response ) ? $response->get_error_message() : wp_remote_retrieve_response_code( $response );
		$out[] = array( 'url' => $url, 'code' => $code );
	}

	update_option(
		DESIGNSTACK_INDEXNOW_LOG,
		array(
			'at'      => current_time( 'mysql' ),
			'results' => $out,
		),
		false
	);

	return $out;
}

/**
 * Сообщает об изменении записи при публикации и при правке опубликованной.
 *
 * @param string  $new  Новый статус.
 * @param string  $old  Прежний статус.
 * @param WP_Post $post Запись.
 * @return void
 */
function designstack_core_indexnow_on_publish( string $new, string $old, WP_Post $post ): void {
	// Импорт создаёт запись раньше её полей, а автосохранение и ревизии не страница вовсе.
	if ( ( defined( 'WP_IMPORTING' ) && WP_IMPORTING ) || wp_is_post_revision( $post ) || wp_is_post_autosave( $post ) ) {
		return;
	}

	if ( 'publish' !== $new || ! in_array( $post->post_type, designstack_core_indexnow_types(), true ) ) {
		return;
	}

	if ( ! designstack_core_is_production() ) {
		return;
	}

	$url = (string) get_permalink( $post );

	if ( $url ) {
		designstack_core_indexnow_submit( array( $url ) );
	}
}
add_action( 'transition_post_status', 'designstack_core_indexnow_on_publish', 10, 3 );

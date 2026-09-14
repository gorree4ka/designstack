<?php
/**
 * Форма «Предложить ресурс»: приём, проверка, черновик, письмо куратору.
 *
 * Без регистрации (D27). Защита — nonce, поле-ловушка и лимит по адресу (US-42).
 * Тексты — docs/VOICE.md, раздел «Форма „Предложить ресурс"».
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

const DESIGNSTACK_CORE_SUGGEST_LIMIT  = 3;
const DESIGNSTACK_CORE_SUGGEST_WINDOW = HOUR_IN_SECONDS;

/**
 * Принимает отправку формы.
 *
 * @return void
 */
function designstack_core_handle_suggest(): void {
	$nonce = isset( $_POST['designstack_suggest_nonce'] )
		? sanitize_text_field( wp_unslash( $_POST['designstack_suggest_nonce'] ) )
		: '';

	if ( ! $nonce || ! wp_verify_nonce( $nonce, 'designstack_suggest' ) ) {
		designstack_core_suggest_back( 'failed', array(), array() );
	}

	// Поле-ловушка заполнено: показываем успех и ничего не пишем.
	if ( ! empty( $_POST['resource_site'] ) ) {
		designstack_core_suggest_thanks();
	}

	$input = array(
		// Адрес возвращается в поле в том виде, в каком его напечатали: esc_url_raw() превращает
		// «excalidraw com» в «http://excalidraw%20com», и человек не видит своей опечатки.
		'resource_url'     => isset( $_POST['resource_url'] ) ? trim( sanitize_text_field( wp_unslash( $_POST['resource_url'] ) ) ) : '',
		'resource_name'    => isset( $_POST['resource_name'] ) ? sanitize_text_field( wp_unslash( $_POST['resource_name'] ) ) : '',
		'resource_comment' => isset( $_POST['resource_comment'] ) ? sanitize_textarea_field( wp_unslash( $_POST['resource_comment'] ) ) : '',
		'resource_email'   => isset( $_POST['resource_email'] ) ? sanitize_email( wp_unslash( $_POST['resource_email'] ) ) : '',
		'resource_consent' => ! empty( $_POST['resource_consent'] ),
	);

	if ( designstack_core_suggest_over_limit() ) {
		designstack_core_suggest_back( 'limit', array(), $input );
	}

	$errors = designstack_core_validate_suggest( $input );

	if ( $errors ) {
		designstack_core_suggest_back( 'error', $errors, $input );
	}

	$known = designstack_core_find_by_url( $input['resource_url'] );

	if ( $known ) {
		designstack_core_suggest_back( 'duplicate', array(), $input, $known );
	}

	$title = $input['resource_name'] ? $input['resource_name'] : (string) wp_parse_url( $input['resource_url'], PHP_URL_HOST );

	// Комментарий посетителя — в тело записи: куратор прочитает его в редакторе
	// и напишет свою оценку в поля «Кому подходит», «За что», «Когда не подойдёт».
	$post_id = wp_insert_post(
		array(
			'post_type'    => 'resource',
			'post_status'  => 'pending',
			'post_title'   => $title,
			'post_content' => $input['resource_comment'],
		),
		true
	);

	if ( is_wp_error( $post_id ) ) {
		designstack_core_suggest_back( 'failed', array(), $input );
	}

	designstack_core_set_field( $post_id, 'url', esc_url_raw( $input['resource_url'] ) );
	update_post_meta( $post_id, '_designstack_suggested_by', $input['resource_email'] );
	designstack_core_count_suggest();
	designstack_core_notify_curator( $post_id, $input );

	designstack_core_suggest_thanks();
}
add_action( 'admin_post_nopriv_designstack_suggest', 'designstack_core_handle_suggest' );
add_action( 'admin_post_designstack_suggest', 'designstack_core_handle_suggest' );

/**
 * Проверяет поля. Ключ ошибки — имя поля, значение — текст словаря.
 *
 * @param array<string, mixed> $input Присланные значения.
 * @return array<string, string>
 */
function designstack_core_validate_suggest( array $input ): array {
	$errors = array();

	// Проверяем только вид адреса. wp_http_validate_url() здесь не годится: она
	// делает DNS-запрос и отбивает домены, которые не резолвятся с сервера, —
	// а каталог как раз собирает и заблокированные сайты.
	$scheme = strtolower( (string) wp_parse_url( $input['resource_url'], PHP_URL_SCHEME ) );
	$host   = (string) wp_parse_url( $input['resource_url'], PHP_URL_HOST );
	$shaped = filter_var( $input['resource_url'], FILTER_VALIDATE_URL )
		&& in_array( $scheme, array( 'http', 'https' ), true )
		&& str_contains( $host, '.' );

	if ( '' === $input['resource_url'] ) {
		$errors['resource_url'] = __( 'Укажи адрес ресурса', 'designstack-core' );
	} elseif ( ! $shaped ) {
		$errors['resource_url'] = __( 'Это не похоже на адрес сайта. Проверь, нет ли пробела или опечатки, например: https://excalidraw.com', 'designstack-core' );
	}

	if ( ! $input['resource_consent'] ) {
		$errors['resource_consent'] = __( 'Без согласия с политикой данных предложение не отправить', 'designstack-core' );
	}

	$length = mb_strlen( $input['resource_comment'] );

	if ( $length > 1000 ) {
		$errors['resource_comment'] = sprintf(
			/* translators: %d — на сколько знаков комментарий длиннее предела. */
			__( 'Комментарий длиннее 1000 знаков на %d — сократи его', 'designstack-core' ),
			$length - 1000
		);
	}

	if ( $input['resource_email'] && ! is_email( $input['resource_email'] ) ) {
		$errors['resource_email'] = __( 'Это не похоже на почту. Проверь адрес или оставь поле пустым', 'designstack-core' );
	}

	return $errors;
}

/**
 * Ресурс с таким адресом уже в каталоге?
 *
 * @param string $url Адрес.
 * @return int Идентификатор записи или 0.
 */
function designstack_core_find_by_url( string $url ): int {
	if ( ! $url ) {
		return 0;
	}

	$host = wp_parse_url( $url, PHP_URL_HOST );

	if ( ! $host ) {
		return 0;
	}

	$found = get_posts(
		array(
			'post_type'      => 'resource',
			'post_status'    => array( 'publish', 'pending', 'draft' ),
			'posts_per_page' => 1,
			'fields'         => 'ids',
			'meta_query'     => array(
				array(
					'key'     => 'url',
					'value'   => str_replace( 'www.', '', (string) $host ),
					'compare' => 'LIKE',
				),
			),
		)
	);

	return $found ? (int) $found[0] : 0;
}

/**
 * Ключ счётчика отправок для этого подключения.
 *
 * Адрес не сохраняем: в ключ идёт только его хеш.
 *
 * @return string
 */
function designstack_core_suggest_key(): string {
	$ip = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : 'unknown';

	return 'designstack_suggest_' . wp_hash( $ip );
}

/**
 * Исчерпан ли лимит отправок за час.
 *
 * @return bool
 */
function designstack_core_suggest_over_limit(): bool {
	return (int) get_transient( designstack_core_suggest_key() ) >= DESIGNSTACK_CORE_SUGGEST_LIMIT;
}

/**
 * Считает отправку.
 *
 * @return void
 */
function designstack_core_count_suggest(): void {
	$key   = designstack_core_suggest_key();
	$count = (int) get_transient( $key );

	set_transient( $key, $count + 1, DESIGNSTACK_CORE_SUGGEST_WINDOW );
}

/**
 * Письмо куратору. Неудача письма не считается сбоем отправки (D66).
 *
 * @param int                  $post_id Черновик.
 * @param array<string, mixed> $input   Присланные значения.
 * @return void
 */
function designstack_core_notify_curator( int $post_id, array $input ): void {
	$subject = sprintf(
		/* translators: %s — название сайта. */
		__( '%s: предложили ресурс', 'designstack-core' ),
		get_bloginfo( 'name' )
	);

	$body = implode(
		"\n",
		array(
			__( 'Через форму предложили ресурс.', 'designstack-core' ),
			'',
			__( 'Адрес:', 'designstack-core' ) . ' ' . $input['resource_url'],
			__( 'Название:', 'designstack-core' ) . ' ' . ( $input['resource_name'] ? $input['resource_name'] : '—' ),
			__( 'Комментарий:', 'designstack-core' ) . ' ' . ( $input['resource_comment'] ? $input['resource_comment'] : '—' ),
			__( 'Обратная почта:', 'designstack-core' ) . ' ' . ( $input['resource_email'] ? $input['resource_email'] : '—' ),
			'',
			__( 'Черновик в очереди:', 'designstack-core' ) . ' ' . get_edit_post_link( $post_id, '' ),
		)
	);

	$sent = wp_mail( designstack_core_curator_email(), $subject, $body );

	if ( defined( 'WP_DEBUG' ) && WP_DEBUG ) {
		error_log( // phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- факт отправки письма нужен в журнале.
			sprintf( 'designstack-core: предложение #%1$d, письмо куратору — %2$s', $post_id, $sent ? 'ушло' : 'не ушло' )
		);
	}
}

/**
 * Возвращает на форму с состоянием и введённым.
 *
 * @param string                $state    error | failed | limit | duplicate.
 * @param array<string, string> $errors   Ошибки полей.
 * @param array<string, mixed>  $input    Введённое.
 * @param int                   $known_id Найденный ресурс для состояния duplicate.
 * @return never
 */
function designstack_core_suggest_back( string $state, array $errors, array $input, int $known_id = 0 ): void {
	$token = wp_generate_password( 12, false );

	set_transient(
		'designstack_suggest_state_' . $token,
		array(
			'state'  => $state,
			'errors' => $errors,
			'input'  => $input,
			'known'  => $known_id,
		),
		5 * MINUTE_IN_SECONDS
	);

	$page = get_page_by_path( 'suggest' );
	$url  = $page ? get_permalink( $page ) : home_url( '/suggest/' );

	wp_safe_redirect( add_query_arg( array( 'suggest' => $state, 'form' => $token ), $url ) . '#ds-suggest-form' );
	exit;
}

/**
 * Уводит на страницу «Спасибо».
 *
 * @return never
 */
function designstack_core_suggest_thanks(): void {
	$page = get_page_by_path( 'suggest/thanks' );
	$url  = $page ? get_permalink( $page ) : home_url( '/suggest/thanks/' );

	wp_safe_redirect( $url );
	exit;
}

/**
 * Состояние формы для текущего запроса.
 *
 * @return array{state: string, errors: array<string, string>, input: array<string, mixed>, known: int}
 */
function designstack_core_suggest_state(): array {
	$empty = array( 'state' => 'default', 'errors' => array(), 'input' => array(), 'known' => 0 );
	$token = isset( $_GET['form'] ) ? sanitize_key( wp_unslash( $_GET['form'] ) ) : '';

	if ( ! $token ) {
		return $empty;
	}

	$saved = get_transient( 'designstack_suggest_state_' . $token );

	return is_array( $saved ) ? array_merge( $empty, $saved ) : $empty;
}

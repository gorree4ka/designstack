<?php
/**
 * Адреса каталога: короткие разделы, статейные рубрики, поиск, редиректы и 404.
 *
 * Целевые адреса — карта URL этапа 07 («Требования к 12»). Механизм проверен
 * пробой `rewrite-short-url` 12.09.2026 (D63, D65).
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Карта «слаг терма типа → корневой адрес раздела».
 *
 * @return array<string, string>
 */
function designstack_core_type_slugs(): array {
	return array(
		'tool'      => 'tools',
		'learning'  => 'learn',
		'asset'     => 'assets',
		'community' => 'community',
	);
}

/**
 * Слаги статейных рубрик: они же корневые адреса разделов.
 *
 * @return array<string, string>
 */
function designstack_core_category_slugs(): array {
	return array(
		'collections' => __( 'Подборки', 'designstack-core' ),
		'digest'      => __( 'Дайджест', 'designstack-core' ),
		'reviews'     => __( 'Обзоры', 'designstack-core' ),
	);
}

/**
 * Правила адресов. Приоритет top: иначе разделы перехватит правило страниц.
 *
 * @return void
 */
function designstack_core_register_rewrite_rules(): void {
	foreach ( designstack_core_type_slugs() as $term => $path ) {
		add_rewrite_rule( '^' . $path . '/?$', 'index.php?resource_type=' . $term, 'top' );
		add_rewrite_rule( '^' . $path . '/page/([0-9]+)/?$', 'index.php?resource_type=' . $term . '&paged=$matches[1]', 'top' );
	}

	$categories = implode( '|', array_keys( designstack_core_category_slugs() ) );
	add_rewrite_rule( '^(' . $categories . ')/?$', 'index.php?category_name=$matches[1]', 'top' );
	add_rewrite_rule( '^(' . $categories . ')/page/([0-9]+)/?$', 'index.php?category_name=$matches[1]&paged=$matches[2]', 'top' );

	// Поиск живёт на /search/?s=…: запрос берётся из строки адреса, а не из пути.
	add_rewrite_rule( '^search/?$', 'index.php?designstack_search=1', 'top' );
	add_rewrite_rule( '^search/page/([0-9]+)/?$', 'index.php?designstack_search=1&paged=$matches[1]', 'top' );
}
add_action( 'init', 'designstack_core_register_rewrite_rules', 10 );

/**
 * Параметры фильтров и служебные переменные запроса.
 *
 * Сами фильтры включает этап 14 — здесь только регистрация имён, чтобы
 * WordPress не терял параметр по дороге.
 *
 * @param array<int, string> $vars Переменные запроса.
 * @return array<int, string>
 */
function designstack_core_query_vars( array $vars ): array {
	$own = array(
		'designstack_search',
		'level',
		'pricing',
		'ru_open',
		'ru_payment',
		'platforms',
		'format',
		'language',
		'license',
		'file_format',
		'cyrillic',
		'platform',
		'is_jobs',
	);

	return array_merge( $vars, $own );
}
add_filter( 'query_vars', 'designstack_core_query_vars' );

/**
 * Превращает /search/ в обычный поиск WordPress по параметру s.
 *
 * @param WP_Query $query Запрос.
 * @return void
 */
function designstack_core_search_query( $query ): void {
	if ( is_admin() || ! $query->is_main_query() || ! $query->get( 'designstack_search' ) ) {
		return;
	}

	$term = isset( $_GET['s'] ) ? sanitize_text_field( wp_unslash( $_GET['s'] ) ) : '';

	$query->set( 's', $term );
	$query->is_search = true;
	$query->is_home   = false;
}
add_action( 'pre_get_posts', 'designstack_core_search_query' );

/**
 * Ссылка терма типа — короткий адрес раздела.
 *
 * @param string  $link     Ссылка.
 * @param WP_Term $term     Терм.
 * @param string  $taxonomy Таксономия.
 * @return string
 */
function designstack_core_term_link( string $link, $term, string $taxonomy ): string {
	if ( 'resource_type' !== $taxonomy ) {
		return $link;
	}

	$slugs = designstack_core_type_slugs();

	return isset( $slugs[ $term->slug ] ) ? home_url( '/' . $slugs[ $term->slug ] . '/' ) : $link;
}
add_filter( 'term_link', 'designstack_core_term_link', 10, 3 );

/**
 * Ссылка рубрики — корневой адрес раздела без /category/.
 *
 * @param string $link    Ссылка.
 * @param int    $term_id Идентификатор терма.
 * @return string
 */
function designstack_core_category_link( string $link, int $term_id ): string {
	$term = get_term( $term_id, 'category' );

	if ( ! $term || is_wp_error( $term ) || ! isset( designstack_core_category_slugs()[ $term->slug ] ) ) {
		return $link;
	}

	return home_url( '/' . $term->slug . '/' );
}
add_filter( 'category_link', 'designstack_core_category_link', 10, 2 );

/**
 * Адрес страницы поиска.
 *
 * @param string $link Ссылка.
 * @return string
 */
function designstack_core_search_link( string $link ): string {
	$term = get_query_var( 's' );

	return home_url( '/search/' ) . ( '' !== $term ? '?s=' . rawurlencode( (string) $term ) : '' );
}
add_filter( 'search_link', 'designstack_core_search_link' );

/**
 * Адрес формы поиска: блок ядра отправляет её на короткий адрес.
 *
 * @param string $form Разметка формы.
 * @return string
 */
function designstack_core_search_form( string $form ): string {
	return str_replace( 'action="' . home_url( '/' ) . '"', 'action="' . home_url( '/search/' ) . '"', $form );
}
add_filter( 'get_search_form', 'designstack_core_search_form' );

/**
 * Постоянные редиректы на канонические адреса карты URL.
 *
 * @return void
 */
function designstack_core_redirects(): void {
	if ( is_admin() || wp_doing_ajax() ) {
		return;
	}

	$target = '';

	// Штатный архив таксономии типа → корневой раздел.
	if ( is_tax( 'resource_type' ) ) {
		$term    = get_queried_object();
		$slugs   = designstack_core_type_slugs();
		$path    = isset( $slugs[ $term->slug ] ) ? $slugs[ $term->slug ] : '';
		$request = isset( $_SERVER['REQUEST_URI'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REQUEST_URI'] ) ) : '';

		if ( $path && str_starts_with( $request, '/resource_type/' ) ) {
			$target = home_url( '/' . $path . '/' );
		}
	}

	// Штатный архив рубрики → корневой раздел.
	if ( ! $target && is_category() ) {
		$term    = get_queried_object();
		$request = isset( $_SERVER['REQUEST_URI'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REQUEST_URI'] ) ) : '';

		if ( isset( designstack_core_category_slugs()[ $term->slug ] ) && str_starts_with( $request, '/category/' ) ) {
			$target = home_url( '/' . $term->slug . '/' );
		}
	}

	// Архив автора: страницы автора в карте нет, а адрес раскрывает логин куратора.
	if ( ! $target && is_author() ) {
		$about  = get_page_by_path( 'about' );
		$target = $about ? get_permalink( $about ) : home_url( '/' );
	}

	// Поиск со штатного адреса → /search/?s=…
	if ( ! $target && isset( $_GET['s'] ) && ! get_query_var( 'designstack_search' ) ) {
		$term = sanitize_text_field( wp_unslash( $_GET['s'] ) );

		if ( is_search() || is_home() ) {
			$target = home_url( '/search/' ) . '?s=' . rawurlencode( $term );
		}
	}

	// Параметр темы вне раздела → архив темы.
	if ( ! $target && is_home() && ! empty( $_GET['topic'] ) ) {
		$slug = sanitize_title( wp_unslash( $_GET['topic'] ) );
		$term = get_term_by( 'slug', $slug, 'topic' );

		if ( $term ) {
			$target = get_term_link( $term );
		}
	}

	if ( $target && ! is_wp_error( $target ) ) {
		wp_safe_redirect( $target, 301 );
		exit;
	}
}
add_action( 'template_redirect', 'designstack_core_redirects', 1 );

/**
 * Адреса, которых в карте нет, отвечают 404, а не угадывают запись.
 *
 * @return void
 */
function designstack_core_force_404(): void {
	if ( is_admin() || wp_doing_ajax() ) {
		return;
	}

	if ( designstack_core_is_forced_404() || is_date() || is_tag() ) {
		global $wp_query;

		$wp_query->set_404();
		status_header( 404 );
		nocache_headers();
	}
}
add_action( 'template_redirect', 'designstack_core_force_404', 0 );

/**
 * Путь, которому положено отвечать 404, а не угадываться и не канонизироваться.
 *
 * @return bool
 */
function designstack_core_is_forced_404(): bool {
	$request = isset( $_SERVER['REQUEST_URI'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REQUEST_URI'] ) ) : '';
	$path    = trim( (string) wp_parse_url( $request, PHP_URL_PATH ), '/' );

	return 'resource' === $path || 1 === preg_match( '#^(level|skill)(/|$)#', $path );
}

/**
 * Отключает угадывание адреса ядром на этих путях.
 *
 * Без этого /resource/ отвечает 301 на страницу серого прототипа `resource-figma`,
 * потому что ядро ищет запись по началу слага (D65).
 *
 * @param bool $guess Пробовать ли угадать.
 * @return bool
 */
function designstack_core_disable_guess( $guess ) {
	return designstack_core_is_forced_404() ? false : $guess;
}
add_filter( 'do_redirect_guess_404_permalink', 'designstack_core_disable_guess' );

/**
 * И сам канонический редирект на этих путях не работает.
 *
 * @param string $redirect Куда ядро собралось увести.
 * @return string|false
 */
function designstack_core_disable_canonical( $redirect ) {
	return designstack_core_is_forced_404() ? false : $redirect;
}
add_filter( 'redirect_canonical', 'designstack_core_disable_canonical' );

/**
 * У записи ровно одна рубрика из трёх: подборка, дайджест или обзор.
 *
 * @param int $post_id Идентификатор записи.
 * @return void
 */
function designstack_core_single_category( int $post_id ): void {
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}

	$known    = array_keys( designstack_core_category_slugs() );
	$assigned = wp_get_object_terms( $post_id, 'category', array( 'fields' => 'slugs' ) );

	if ( is_wp_error( $assigned ) ) {
		return;
	}

	$ours = array_values( array_intersect( $assigned, $known ) );

	if ( count( $ours ) > 1 || ( $ours && count( $assigned ) > count( $ours ) ) ) {
		wp_set_object_terms( $post_id, $ours[0], 'category', false );
	}
}
add_action( 'save_post_post', 'designstack_core_single_category', 20 );

/**
 * Заводит рубрики статейных форматов. Вызывается при активации.
 *
 * @return int Сколько рубрик создано.
 */
function designstack_core_install_categories(): int {
	$created = 0;

	foreach ( designstack_core_category_slugs() as $slug => $name ) {
		if ( term_exists( $slug, 'category' ) ) {
			continue;
		}

		$result = wp_insert_term( $name, 'category', array( 'slug' => $slug ) );

		if ( ! is_wp_error( $result ) ) {
			++$created;
		}
	}

	return $created;
}

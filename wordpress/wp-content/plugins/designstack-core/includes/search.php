<?php
/**
 * Поиск по каталогу: к названию и тексту добавляются вердикт и оценка куратора.
 *
 * Встроенный поиск WordPress смотрит только в заголовок и содержимое записи, а у ресурса
 * и то и другое почти пустое: всё, что человек ищет словами, лежит в полях `verdict`
 * и трёх частях оценки. Поэтому к запросу добавляется присоединение таблицы полей —
 * стандартный для WordPress способ расширить поиск (фильтры `posts_join`, `posts_search`,
 * `posts_distinct`), а не свой SQL-запрос.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Поля, по которым ищем помимо заголовка и текста.
 *
 * @return array<int, string>
 */
function designstack_core_search_fields(): array {
	return array( 'verdict', 'review_for', 'review_why', 'review_not' );
}

/**
 * Это главный поиск по сайту?
 *
 * @param WP_Query $query Запрос.
 * @return bool
 */
function designstack_core_is_site_search( WP_Query $query ): bool {
	return ! is_admin() && $query->is_main_query() && $query->is_search() && '' !== (string) $query->get( 's' );
}

/**
 * Присоединяет поля записи к поиску.
 *
 * @param string   $join  Часть запроса.
 * @param WP_Query $query Запрос.
 * @return string
 */
function designstack_core_search_join( $join, $query ) {
	global $wpdb;

	if ( ! $query instanceof WP_Query || ! designstack_core_is_site_search( $query ) ) {
		return $join;
	}

	$keys = designstack_core_search_fields();
	$in   = implode( ', ', array_fill( 0, count( $keys ), '%s' ) );

	// phpcs:ignore WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- имена полей подставлены через prepare ниже.
	$join .= $wpdb->prepare(
		" LEFT JOIN {$wpdb->postmeta} AS ds_search ON ( {$wpdb->posts}.ID = ds_search.post_id AND ds_search.meta_key IN ( {$in} ) ) ",
		...$keys
	);

	return $join;
}
add_filter( 'posts_join', 'designstack_core_search_join', 10, 2 );

/**
 * Добавляет к условию поиска совпадение по полям.
 *
 * @param string   $search Часть запроса.
 * @param WP_Query $query  Запрос.
 * @return string
 */
function designstack_core_search_where( $search, $query ) {
	global $wpdb;

	if ( '' === $search || ! $query instanceof WP_Query || ! designstack_core_is_site_search( $query ) ) {
		return $search;
	}

	$terms = $query->get( 'search_terms' );

	if ( ! $terms ) {
		$terms = array( (string) $query->get( 's' ) );
	}

	$extra = '';

	foreach ( (array) $terms as $term ) {
		$like   = '%' . $wpdb->esc_like( (string) $term ) . '%';
		$extra .= $wpdb->prepare( ' OR ( ds_search.meta_value LIKE %s )', $like );
	}

	// Условие ядра приходит вида « AND (((…)))» — своё дописываем внутрь общей скобки.
	return ' AND ( ' . preg_replace( '/^\s*AND\s*/', '', $search ) . $extra . ' ) ';
}
add_filter( 'posts_search', 'designstack_core_search_where', 10, 2 );

/**
 * Одна запись — одна строка выдачи: полей у записи несколько.
 *
 * @param string   $distinct Часть запроса.
 * @param WP_Query $query    Запрос.
 * @return string
 */
function designstack_core_search_distinct( $distinct, $query ) {
	if ( ! $query instanceof WP_Query || ! designstack_core_is_site_search( $query ) ) {
		return $distinct;
	}

	return 'DISTINCT';
}
add_filter( 'posts_distinct', 'designstack_core_search_distinct', 10, 2 );

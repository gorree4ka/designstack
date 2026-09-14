<?php
/**
 * Выгрузка каталога в JSON для скриптов проверки.
 *
 * Запуск: tools/wp.cmd --path=wordpress eval-file C:/Projects/DesignSite/scripts/export_resources.php
 * Печатает массив записей `resource` с полями, которые нужны перепроверке (директива 16, фаза 6).
 * Ничего не меняет: только чтение.
 *
 * @package designstack
 */

defined( 'ABSPATH' ) || exit;

$ds_posts = get_posts(
	array(
		'post_type'   => 'resource',
		'post_status' => array( 'publish', 'draft', 'pending' ),
		'numberposts' => -1,
		'orderby'     => 'title',
		'order'       => 'ASC',
	)
);

$ds_out = array();

foreach ( $ds_posts as $ds_post ) {
	$ds_types = wp_get_post_terms( $ds_post->ID, 'resource_type', array( 'fields' => 'slugs' ) );

	$ds_out[] = array(
		'id'         => $ds_post->ID,
		'slug'       => $ds_post->post_name,
		'title'      => $ds_post->post_title,
		'status'     => $ds_post->post_status,
		'type'       => is_wp_error( $ds_types ) ? '' : ( $ds_types[0] ?? '' ),
		'url'        => (string) get_post_meta( $ds_post->ID, 'url', true ),
		'checked_at' => (string) get_post_meta( $ds_post->ID, 'checked_at', true ),
		'state'      => (string) get_post_meta( $ds_post->ID, 'status', true ),
		'ru_open'    => (string) get_post_meta( $ds_post->ID, 'ru_open', true ),
		'ru_payment' => (string) get_post_meta( $ds_post->ID, 'ru_payment', true ),
		'pricing'    => (string) get_post_meta( $ds_post->ID, 'pricing', true ),
		'price_note' => (string) get_post_meta( $ds_post->ID, 'price_note', true ),
		'curator'    => (string) get_post_meta( $ds_post->ID, 'curator', true ),
		'analogs'    => array_values( array_filter( array_map( 'absint', (array) get_post_meta( $ds_post->ID, 'ru_alternative', true ) ) ) ),
	);
}

echo wp_json_encode( $ds_out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES );

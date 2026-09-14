<?php
/**
 * Колонки списка ресурсов в админке.
 *
 * Куратору нужно с одного экрана видеть тип, доступ, оплату, состояние и дату проверки.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Добавляет колонки в список записей.
 *
 * @param array<string, string> $columns Колонки.
 * @return array<string, string>
 */
function designstack_core_resource_columns( array $columns ): array {
	$new = array();

	foreach ( $columns as $key => $label ) {
		$new[ $key ] = $label;

		if ( 'title' === $key ) {
			$new['ds_ru_open']    = __( 'Доступ из РФ', 'designstack-core' );
			$new['ds_ru_payment'] = __( 'Оплата из РФ', 'designstack-core' );
			$new['ds_status']     = __( 'Состояние', 'designstack-core' );
			$new['ds_checked_at'] = __( 'Дата проверки', 'designstack-core' );
		}
	}

	return $new;
}
add_filter( 'manage_resource_posts_columns', 'designstack_core_resource_columns' );

/**
 * Выводит значение колонки словом словаря.
 *
 * @param string $column  Ключ колонки.
 * @param int    $post_id Идентификатор записи.
 * @return void
 */
function designstack_core_resource_column( string $column, int $post_id ): void {
	$map = array(
		'ds_ru_open'    => 'ru_open',
		'ds_ru_payment' => 'ru_payment',
		'ds_status'     => 'status',
	);

	if ( isset( $map[ $column ] ) ) {
		$key   = $map[ $column ];
		$value = (string) get_post_meta( $post_id, $key, true );
		$label = designstack_core_enum_label( $key, $value );

		echo $label ? esc_html( $label ) : '<span aria-hidden="true">—</span><span class="screen-reader-text">' . esc_html__( 'не заполнено', 'designstack-core' ) . '</span>';

		return;
	}

	if ( 'ds_checked_at' === $column ) {
		$date = (string) get_post_meta( $post_id, 'checked_at', true );

		if ( ! $date ) {
			echo '<span aria-hidden="true">—</span><span class="screen-reader-text">' . esc_html__( 'не проверяли', 'designstack-core' ) . '</span>';

			return;
		}

		$stale = strtotime( $date ) < strtotime( '-90 days' );

		printf(
			'<span%1$s>%2$s</span>',
			$stale ? ' title="' . esc_attr__( 'Давно не проверяли', 'designstack-core' ) . '"' : '',
			esc_html( mysql2date( 'j M Y', $date . ' 00:00:00' ) )
		);
	}
}
add_action( 'manage_resource_posts_custom_column', 'designstack_core_resource_column', 10, 2 );

/**
 * Разрешает сортировку по дате проверки и состоянию.
 *
 * @param array<string, string> $columns Сортируемые колонки.
 * @return array<string, string>
 */
function designstack_core_resource_sortable( array $columns ): array {
	$columns['ds_checked_at'] = 'ds_checked_at';
	$columns['ds_status']     = 'ds_status';

	return $columns;
}
add_filter( 'manage_edit-resource_sortable_columns', 'designstack_core_resource_sortable' );

/**
 * Переводит сортировку колонок в запрос по мета-полю.
 *
 * @param WP_Query $query Запрос списка записей.
 * @return void
 */
function designstack_core_resource_orderby( $query ): void {
	if ( ! is_admin() || ! $query->is_main_query() ) {
		return;
	}

	$orderby = $query->get( 'orderby' );
	$map     = array(
		'ds_checked_at' => 'checked_at',
		'ds_status'     => 'status',
	);

	if ( isset( $map[ $orderby ] ) ) {
		$query->set( 'meta_key', $map[ $orderby ] );
		$query->set( 'orderby', 'meta_value' );
	}
}
add_action( 'pre_get_posts', 'designstack_core_resource_orderby' );

<?php
/**
 * Разметка блока «Список ресурсов».
 *
 * Два источника. `manual` — выборка по атрибутам: так куратор собирает подборку или выпуск.
 * `archive` — записи основного запроса: раздел, тема, страница выдачи. Второй режим только читает
 * текущий запрос и не строит выборку по параметрам — фильтры включает этап 14.
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_source = 'archive' === ( $attributes['source'] ?? 'manual' ) ? 'archive' : 'manual';
$ds_layout = 'list' === ( $attributes['layout'] ?? 'grid' ) ? 'list' : 'grid';
$ds_posts  = array();

$ds_empty_title = __( 'В подборке пока нет ресурсов', 'designstack-core' );

if ( 'archive' === $ds_source ) {
	global $wp_query;

	foreach ( (array) $wp_query->posts as $ds_item ) {
		if ( $ds_item instanceof WP_Post && 'resource' === $ds_item->post_type ) {
			$ds_posts[] = $ds_item;
		}
	}

	$ds_term = function_exists( 'designstack_core_archive_term' ) ? designstack_core_archive_term() : null;

	if ( $ds_term && 'topic' === $ds_term->taxonomy ) {
		$ds_empty_title = __( 'В этой теме пока нет ресурсов', 'designstack-core' );
	} elseif ( $ds_term ) {
		$ds_empty_title = __( 'В разделе пока нет ресурсов', 'designstack-core' );
	}
} else {
	$ds_ids     = array_map( 'absint', (array) ( $attributes['ids'] ?? array() ) );
	$ds_limit   = min( 24, max( 6, absint( $attributes['limit'] ?? 12 ) ) );
	$ds_orderby = (string) ( $attributes['orderby'] ?? 'checked_at' );

	$ds_args = array(
		'post_type'      => 'resource',
		'post_status'    => 'publish',
		'posts_per_page' => $ds_limit,
		'no_found_rows'  => true,
	);

	if ( $ds_ids ) {
		// orderby => post__in работает только вместе с post__in.
		$ds_args['post__in'] = $ds_ids;
		$ds_args['orderby']  = 'post__in';
	} else {
		$ds_tax = array();

		foreach ( array( 'resource_type', 'topic', 'level' ) as $ds_taxonomy ) {
			$ds_value = sanitize_key( (string) ( $attributes[ $ds_taxonomy ] ?? '' ) );

			if ( $ds_value ) {
				$ds_tax[] = array(
					'taxonomy' => $ds_taxonomy,
					'field'    => 'slug',
					'terms'    => $ds_value,
				);
			}
		}

		if ( count( $ds_tax ) > 1 ) {
			$ds_tax['relation'] = 'AND';
		}

		if ( $ds_tax ) {
			$ds_args['tax_query'] = $ds_tax;
		}

		$ds_meta = array();

		foreach ( array( 'pricing', 'ru_open', 'ru_payment' ) as $ds_key ) {
			$ds_value = sanitize_key( (string) ( $attributes[ $ds_key ] ?? '' ) );

			if ( $ds_value && designstack_core_enum_label( $ds_key, $ds_value ) ) {
				$ds_meta[] = array(
					'key'     => $ds_key,
					'value'   => $ds_value,
					'compare' => '=',
				);
			}
		}

		if ( count( $ds_meta ) > 1 ) {
			$ds_meta['relation'] = 'AND';
		}

		if ( $ds_meta ) {
			$ds_args['meta_query'] = $ds_meta;
		}

		if ( 'checked_at' === $ds_orderby ) {
			$ds_args['meta_key'] = 'checked_at';
			$ds_args['orderby']  = 'meta_value';
			$ds_args['order']    = 'DESC';
		} elseif ( 'title' === $ds_orderby ) {
			$ds_args['orderby'] = 'title';
			$ds_args['order']   = 'ASC';
		} else {
			$ds_args['orderby'] = 'date';
			$ds_args['order']   = 'DESC';
		}
	}

	$ds_query = new WP_Query( $ds_args );
	$ds_posts = $ds_query->posts;
}

if ( ! $ds_posts ) {
	if ( 'archive' === $ds_source ) {
		// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- разметка собрана с экранированием внутри.
		echo designstack_core_render_empty_archive();

		return;
	}

	// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- разметка собрана с экранированием внутри, kses вырезал бы svg иконок.
	echo designstack_core_render_empty(
		'section',
		$ds_empty_title,
		'',
		sprintf(
			'<a class="ds-link" href="%1$s">%2$s</a>',
			esc_url( home_url( '/suggest/' ) ),
			esc_html__( 'Предложить ресурс', 'designstack-core' )
		)
	);

	return;
}

$ds_cards = '';

foreach ( $ds_posts as $ds_post ) {
	// В архиве список идёт сразу под H1 страницы; в записи уровень считается от того,
	// что куратор написал выше блока.
	$ds_cards .= designstack_core_render_card(
		(int) $ds_post->ID,
		'archive' === $ds_source ? 2 : designstack_core_heading_level()
	);
}

$ds_wrapper = get_block_wrapper_attributes(
	array( 'class' => 'ds-resource-list ds-resource-list--' . $ds_layout )
);

// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- экранирование сделано в designstack_core_render_card().
printf( '<div %1$s>%2$s</div>', $ds_wrapper, $ds_cards );

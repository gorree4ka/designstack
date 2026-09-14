<?php
/**
 * Разметка блока «Доступ и оплата из РФ».
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_post_id = absint( $block->context['postId'] ?? get_the_ID() );

if ( ! $ds_post_id || 'resource' !== get_post_type( $ds_post_id ) ) {
	return;
}

$ds_out = '';

foreach ( array( 'ru_open', 'ru_payment' ) as $ds_key ) {
	$ds_value = (string) designstack_core_get_field( $ds_post_id, $ds_key );

	if ( ! $ds_value ) {
		continue;
	}

	// У бесплатного ресурса метки оплаты нет (D28).
	if ( 'ru_payment' === $ds_key && 'free' === designstack_core_get_field( $ds_post_id, 'pricing' ) ) {
		continue;
	}

	list( $ds_variant, $ds_icon ) = designstack_core_status_look( $ds_key, $ds_value );
	$ds_out                      .= designstack_core_badge( designstack_core_enum_label( $ds_key, $ds_value ), $ds_variant, $ds_icon );
}

if ( ! empty( $attributes['showState'] ) ) {
	list( $ds_state, $ds_state_variant, $ds_state_icon ) = designstack_core_state( $ds_post_id );

	if ( $ds_state ) {
		$ds_out .= designstack_core_badge( $ds_state, $ds_state_variant, $ds_state_icon );
	}
}

if ( ! $ds_out ) {
	return;
}

// Размер метки в каталоге паттернов один: класса под второй размер нет, и мы его не заводим.
$ds_wrapper = get_block_wrapper_attributes( array( 'class' => 'ds-badges' ) );
$ds_checked = ! empty( $attributes['showChecked'] ) ? designstack_core_checked_line( $ds_post_id ) : '';

// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- метки собраны с экранированием, kses вырезал бы svg.
printf( '<div %1$s>%2$s</div>', $ds_wrapper, $ds_out );

if ( $ds_checked ) {
	printf( '<p class="ds-meta ds-meta--xs">%s</p>', esc_html( $ds_checked ) );
}

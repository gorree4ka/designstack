<?php
/**
 * Разметка блока «Есть в уроках» на странице ресурса (D197).
 *
 * Уроки находятся по полю `lesson_reads`: его пересчитывает сохранение урока из раздела
 * «Что почитать дальше». Связь идёт в обе стороны — урок советует ресурс, а ресурс показывает,
 * после каких уроков его читать.
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_id = isset( $block->context['postId'] ) ? (int) $block->context['postId'] : get_queried_object_id();

if ( ! $ds_id || 'resource' !== get_post_type( $ds_id ) ) {
	return;
}

$ds_lessons = designstack_core_lessons_for_resource( (string) get_post_field( 'post_name', $ds_id ) );

if ( ! $ds_lessons ) {
	return;
}

$ds_rows = '';

foreach ( $ds_lessons as $ds_one ) {
	$ds_rows .= '<li class="ds-lessons__row"><span class="ds-lessons__step">' . esc_html( $ds_one['label'] ) . '</span>'
		. '<a class="ds-lessons__link" href="' . esc_url( $ds_one['url'] ) . '">' . esc_html( $ds_one['title'] ) . '</a></li>';
}

printf(
	'<section class="ds-lessons-ref" aria-labelledby="ds-lessons-ref-title"><h2 class="ds-section__title" id="ds-lessons-ref-title">%1$s</h2><p class="ds-lessons-ref__sub">%2$s</p><ul class="ds-lessons__list">%3$s</ul></section>',
	esc_html__( 'Есть в уроках', 'designstack-core' ),
	esc_html__( 'Этот ресурс советуют прочитать после уроков ниже.', 'designstack-core' ),
	$ds_rows // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — строки собраны выше с экранированием.
);

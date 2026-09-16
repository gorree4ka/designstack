<?php
/**
 * Разметка блока «Шапка урока».
 *
 * Показывает, где человек находится в карте: область, навык и на какую ступень
 * поднимает этот урок. Три метки ступеней стоят всегда — так видно, что тема
 * продолжается, и урок не выглядит единственным.
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_id = isset( $block->context['postId'] ) ? (int) $block->context['postId'] : get_the_ID();

if ( ! $ds_id ) {
	return;
}

$ds_step  = (string) get_post_meta( $ds_id, 'lesson_step', true );
$ds_terms = wp_get_post_terms( $ds_id, 'skill' );
$ds_skill = ( ! is_wp_error( $ds_terms ) && $ds_terms ) ? $ds_terms[0] : null;
$ds_area  = ( $ds_skill && $ds_skill->parent ) ? get_term( $ds_skill->parent, 'skill' ) : null;

$ds_out = '<div class="ds-page-header">';

if ( $ds_skill ) {
	$ds_out .= '<p class="ds-page-header__kicker">' . esc_html(
		designstack_core_join(
			array_filter(
				array(
					$ds_area && ! is_wp_error( $ds_area ) ? $ds_area->name : '',
					$ds_skill->name,
				)
			)
		)
	) . '</p>';
}

if ( $ds_step ) {
	// Метки выглядят как переключатель ступеней, поэтому они им и работают: ступень
	// с готовым уроком — ссылка, ненаписанная — погашенная метка с пояснением для чтеца.
	$ds_lessons = $ds_skill ? designstack_core_lessons_map() : array();
	$ds_lessons = isset( $ds_lessons[ $ds_skill->slug ] ) ? $ds_lessons[ $ds_skill->slug ] : array();

	$ds_out .= '<ul class="ds-lesson__levels">';

	foreach ( array( 'junior', 'middle', 'senior' ) as $ds_one ) {
		$ds_is    = $ds_one === $ds_step;
		$ds_label = esc_html( designstack_core_step_label( $ds_one ) );
		$ds_url   = ( ! $ds_is && isset( $ds_lessons[ $ds_one ] ) ) ? $ds_lessons[ $ds_one ] : '';

		// Внутренний элемент есть всегда: на нём лежат отступы, поэтому у ссылки нажимается вся метка, а не только буквы.
		if ( $ds_is ) {
			$ds_body = '<span class="ds-lesson__level-body">' . $ds_label
				. '<span class="screen-reader-text"> — ступень этого урока</span></span>';
		} elseif ( $ds_url ) {
			$ds_body = '<a class="ds-lesson__level-body" href="' . esc_url( $ds_url ) . '">' . $ds_label . '</a>';
		} else {
			$ds_body = '<span class="ds-lesson__level-body">' . $ds_label
				. '<span class="screen-reader-text"> — урок пишется</span></span>';
		}

		$ds_out .= '<li class="ds-lesson__level'
			. ( $ds_is ? ' is-current' : '' )
			. ( ! $ds_is && ! $ds_url ? ' is-soon' : '' )
			. '">' . $ds_body . '</li>';
	}

	$ds_out .= '</ul>';
}

$ds_out .= '<h1 class="ds-page-header__title">' . esc_html( get_the_title( $ds_id ) ) . '</h1>';

$ds_lead = (string) get_post_field( 'post_excerpt', $ds_id );

if ( $ds_lead ) {
	$ds_out .= '<p class="ds-page-header__lead">' . esc_html( $ds_lead ) . '</p>';
}

$ds_out .= '</div>';

echo $ds_out; // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — разметка собрана выше с экранированием каждой части.

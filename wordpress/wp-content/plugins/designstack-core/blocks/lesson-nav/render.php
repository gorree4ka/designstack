<?php
/**
 * Разметка блока «Что дальше после урока».
 *
 * Урок читают двадцать пять минут, и до этой правки последней строкой был список книг,
 * а за ней сразу подвал сайта. Здесь человек либо идёт на следующую ступень того же
 * навыка, либо возвращается в карту развития — другого выхода со страницы урока нет.
 *
 * Если урок следующей ступени ещё не написан, об этом сказано прямо: обещание без
 * работающей страницы — битая ссылка (то же правило у баннера проверки и у карты).
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_id = isset( $block->context['postId'] ) ? (int) $block->context['postId'] : get_the_ID();

if ( ! $ds_id || 'lesson' !== get_post_type( $ds_id ) ) {
	return;
}

$ds_step  = (string) get_post_meta( $ds_id, 'lesson_step', true );
$ds_terms = wp_get_post_terms( $ds_id, 'skill' );
$ds_skill = ( ! is_wp_error( $ds_terms ) && $ds_terms ) ? $ds_terms[0] : null;

$ds_after = array(
	'junior' => 'middle',
	'middle' => 'senior',
);

$ds_next = isset( $ds_after[ $ds_step ] ) ? $ds_after[ $ds_step ] : '';
$ds_url  = '';
$ds_name = '';

// Уроки навыка берём запросом по таксономии и отбираем ступень в PHP: их три штуки на навык,
// а `meta_query` на SQLite проверять дороже, чем обойтись без неё.
if ( $ds_next && $ds_skill ) {
	$ds_siblings = get_posts(
		array(
			'post_type'      => 'lesson',
			'post_status'    => 'publish',
			'posts_per_page' => 10,
			'post__not_in'   => array( $ds_id ),
			'tax_query'      => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_tax_query — один запрос на страницу урока.
				array(
					'taxonomy' => 'skill',
					'field'    => 'term_id',
					'terms'    => $ds_skill->term_id,
				),
			),
		)
	);

	foreach ( $ds_siblings as $ds_one ) {
		if ( $ds_next === (string) get_post_meta( $ds_one->ID, 'lesson_step', true ) ) {
			$ds_url  = (string) get_permalink( $ds_one );
			$ds_name = (string) get_the_title( $ds_one );
			break;
		}
	}
}

$ds_map = get_page_by_path( 'map' );
$ds_map = ( $ds_map && 'publish' === $ds_map->post_status ) ? (string) get_permalink( $ds_map ) : '';

if ( ! $ds_next && ! $ds_map ) {
	return;
}

$ds_out = '<nav class="ds-lesson-nav" aria-label="' . esc_attr__( 'Что дальше', 'designstack-core' ) . '">';

if ( $ds_url ) {
	$ds_out .= '<a class="ds-lesson-nav__next" href="' . esc_url( $ds_url ) . '" data-track="lesson-next" data-track-source="' . esc_attr( $ds_step ) . '">'
		. '<span class="ds-lesson-nav__kicker">' . esc_html(
			sprintf(
				/* translators: %s — название ступени. */
				__( 'Следующая ступень · %s', 'designstack-core' ),
				designstack_core_step_label( $ds_next )
			)
		) . '</span>'
		. '<span class="ds-lesson-nav__title">' . esc_html( $ds_name ) . '</span>'
		. '</a>';
} elseif ( $ds_next ) {
	$ds_out .= '<p class="ds-lesson-nav__soon">'
		. '<span class="ds-lesson-nav__kicker">' . esc_html(
			sprintf(
				/* translators: %s — название ступени. */
				__( 'Следующая ступень · %s', 'designstack-core' ),
				designstack_core_step_label( $ds_next )
			)
		) . '</span>'
		. '<span class="ds-lesson-nav__title">' . esc_html__( 'Урок пишется', 'designstack-core' ) . '</span>'
		. '</p>';
} else {
	$ds_out .= '<p class="ds-lesson-nav__soon">'
		. '<span class="ds-lesson-nav__kicker">' . esc_html__( 'Последняя ступень', 'designstack-core' ) . '</span>'
		. '<span class="ds-lesson-nav__title">' . esc_html__( 'Навык пройден целиком', 'designstack-core' ) . '</span>'
		. '</p>';
}

if ( $ds_map ) {
	$ds_out .= '<a class="ds-button ds-button--secondary ds-lesson-nav__map" href="' . esc_url( $ds_map ) . '" data-track="lesson-map">'
		. esc_html__( 'Открыть карту развития', 'designstack-core' ) . '</a>';
}

$ds_out .= '</nav>';

echo $ds_out; // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — разметка собрана выше с экранированием каждой части.

<?php
/**
 * Разметка блока «Все уроки» — страница `/lessons/` (D197).
 *
 * Области и навыки идут в порядке карты развития, под навыком — написанные уроки по ступеням.
 * Ссылка на урок — его полное название: по подписи «Урок на Junior» поисковик не понимает,
 * о чём урок, а по названию понимает (лист решений P30). Ненаписанных уроков здесь нет:
 * они видны на карте, и ссылка на неё стоит внизу.
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_areas = designstack_core_skills_map();
$ds_index = designstack_core_lessons_index();

if ( ! $ds_areas || ! $ds_index ) {
	return;
}

$ds_check = get_page_by_path( 'grade-check' );
$ds_map   = get_page_by_path( 'map' );
$ds_ready = 0;

foreach ( $ds_index as $ds_steps ) {
	$ds_ready += count( $ds_steps );
}

$ds_out  = '<div class="ds-lessons">';
$ds_out .= '<p class="ds-page-header__lead">' . esc_html( designstack_core_lessons_lead() ) . '</p>';

if ( $ds_check && 'publish' === $ds_check->post_status ) {
	$ds_out .= '<div class="ds-map__intro"><p class="ds-map__state">'
		. esc_html__( 'Не знаете, с какой ступени начать? Пройдите проверку грейда — карта развития отметит ваш урок по каждому навыку.', 'designstack-core' )
		. '</p><p><a class="ds-button ds-button--primary" href="' . esc_url( (string) get_permalink( $ds_check ) ) . '">'
		. esc_html__( 'Проверить свой грейд', 'designstack-core' ) . '</a></p></div>';
}

$ds_sections = '';
$ds_chips    = '';

foreach ( $ds_areas as $ds_area ) {
	$ds_items = '';

	foreach ( $ds_area['skills'] as $ds_skill ) {
		$ds_slug = (string) $ds_skill['slug'];

		if ( empty( $ds_index[ $ds_slug ] ) ) {
			continue;
		}

		$ds_rows = '';

		foreach ( array( 'junior', 'middle', 'senior' ) as $ds_step ) {
			if ( empty( $ds_index[ $ds_slug ][ $ds_step ] ) ) {
				continue;
			}

			$ds_one   = $ds_index[ $ds_slug ][ $ds_step ];
			$ds_rows .= '<li class="ds-lessons__row"><span class="ds-lessons__step">' . esc_html( designstack_core_step_label( $ds_step ) ) . '</span>'
				. '<a class="ds-lessons__link" href="' . esc_url( $ds_one['url'] ) . '">' . esc_html( $ds_one['title'] ) . '</a></li>';
		}

		$ds_items .= '<li class="ds-map__item ds-lessons__item"><div class="ds-map__body">'
			. '<h3 class="ds-map__name">' . esc_html( $ds_skill['name'] ) . '</h3>'
			. '<p class="ds-map__hint">' . esc_html( $ds_skill['hint'] ) . '</p></div>'
			. '<ul class="ds-lessons__list">' . $ds_rows . '</ul></li>';
	}

	if ( '' === $ds_items ) {
		continue;
	}

	$ds_anchor    = 'area-' . sanitize_title( (string) $ds_area['slug'] );
	$ds_chips    .= '<li><a class="ds-lessons__area-link" href="#' . esc_attr( $ds_anchor ) . '">' . esc_html( $ds_area['name'] ) . '</a></li>';
	$ds_sections .= '<section class="ds-map__area" id="' . esc_attr( $ds_anchor ) . '">'
		. '<h2 class="ds-map__area-name">' . esc_html( $ds_area['name'] ) . '</h2>'
		. '<ul class="ds-map__list">' . $ds_items . '</ul></section>';
}

$ds_out .= '<nav class="ds-lessons__areas" aria-label="' . esc_attr__( 'Области', 'designstack-core' ) . '"><ul>' . $ds_chips . '</ul></nav>';
$ds_out .= $ds_sections;

$ds_total = designstack_core_skills_count() * 3;
$ds_line  = sprintf(
	/* translators: 1 — сколько уроков написано, 2 — сколько всего. */
	esc_html__( 'Уроков готово: %1$d из %2$d. Какие пишутся, видно на карте развития.', 'designstack-core' ),
	(int) $ds_ready,
	(int) $ds_total
);

if ( $ds_map && 'publish' === $ds_map->post_status ) {
	$ds_line = str_replace(
		esc_html__( 'карте развития', 'designstack-core' ),
		'<a class="ds-link" href="' . esc_url( (string) get_permalink( $ds_map ) ) . '">' . esc_html__( 'карте развития', 'designstack-core' ) . '</a>',
		$ds_line
	);
}

$ds_out .= '<p class="ds-map__count">' . $ds_line . '</p>';
$ds_out .= '</div>';

echo $ds_out; // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — разметка собрана выше с экранированием каждой части.

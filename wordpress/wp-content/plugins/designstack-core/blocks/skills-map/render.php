<?php
/**
 * Разметка блока «Карта развития».
 *
 * Все 37 навыков по областям. Сервер рисует карту целиком со ссылками на все написанные уроки;
 * ступень конкретного человека знает только его браузер — ответы проверки грейда лежат в
 * localStorage (D18: регистрации на сайте нет). Поэтому скрипт подставляет каждому навыку его
 * ступень и открывает нужную кнопку, а без скрипта видна честная полная карта.
 *
 * Грейд варианта ответа отдаём в `data-grades`: без него браузер не переведёт сохранённый
 * номер ответа в ступень. На проверке грейда так делать нельзя (D142) — там подсказка ломает
 * измерение, — но здесь измерение уже позади.
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_areas = designstack_core_skills_map();

if ( ! $ds_areas ) {
	return;
}

$ds_lessons = designstack_core_lessons_map();
$ds_check   = get_page_by_path( 'grade-check' );
$ds_ready   = 0;

foreach ( $ds_lessons as $ds_one ) {
	$ds_ready += count( $ds_one );
}

$ds_total = designstack_core_skills_count() * 3;

$ds_out  = '<div class="ds-map" data-map>';
$ds_out .= '<div class="ds-map__intro" data-map-intro>';
$ds_out .= '<p class="ds-map__state" data-map-state>'
	. esc_html__( 'Карта показана целиком. Пройдите проверку грейда — и здесь отметится ваша ступень по каждому навыку, а кнопка поведёт на нужный урок.', 'designstack-core' )
	. '</p>';

if ( $ds_check && 'publish' === $ds_check->post_status ) {
	$ds_out .= '<p><a class="ds-button ds-button--primary" href="' . esc_url( (string) get_permalink( $ds_check ) ) . '" data-map-check>'
		. esc_html__( 'Проверить свой грейд', 'designstack-core' ) . '</a></p>';
}

$ds_out .= '</div>';

$ds_out .= '<p class="ds-map__count">' . sprintf(
	/* translators: 1 — сколько уроков написано, 2 — сколько всего. */
	esc_html__( 'Уроков готово: %1$d из %2$d. Остальные пишутся — на карте они помечены.', 'designstack-core' ),
	(int) $ds_ready,
	(int) $ds_total
) . '</p>';

foreach ( $ds_areas as $ds_area ) {
	$ds_out .= '<section class="ds-map__area">';
	$ds_out .= '<h2 class="ds-map__area-name">' . esc_html( $ds_area['name'] ) . '</h2>';
	$ds_out .= '<ul class="ds-map__list">';

	foreach ( $ds_area['skills'] as $ds_skill ) {
		$ds_slug   = (string) $ds_skill['slug'];
		$ds_grades = array();

		foreach ( $ds_skill['opts'] as $ds_opt ) {
			$ds_grades[] = (string) $ds_opt['grade'];
		}

		$ds_out .= '<li class="ds-map__item" data-map-skill="' . esc_attr( $ds_slug ) . '"'
			. ' data-grades="' . esc_attr( implode( ',', $ds_grades ) ) . '">';
		$ds_out .= '<div class="ds-map__body">';
		$ds_out .= '<h3 class="ds-map__name">' . esc_html( $ds_skill['name'] ) . '</h3>';
		$ds_out .= '<p class="ds-map__hint">' . esc_html( $ds_skill['hint'] ) . '</p>';
		$ds_out .= '<p class="ds-map__step" data-map-step hidden></p>';
		$ds_out .= '</div>';

		$ds_out .= '<div class="ds-map__steps">';

		foreach ( array( 'junior', 'middle', 'senior' ) as $ds_step ) {
			$ds_url  = isset( $ds_lessons[ $ds_slug ][ $ds_step ] ) ? $ds_lessons[ $ds_slug ][ $ds_step ] : '';
			$ds_name = designstack_core_step_label( $ds_step );

			if ( $ds_url ) {
				$ds_out .= '<a class="ds-map__lesson" href="' . esc_url( $ds_url ) . '" data-map-lesson="' . esc_attr( $ds_step ) . '">'
					. sprintf(
						/* translators: %s — ступень: Junior, Middle или Senior. */
						esc_html__( 'Урок на %s', 'designstack-core' ),
						esc_html( $ds_name )
					) . '</a>';
			} else {
				$ds_out .= '<span class="ds-map__lesson ds-map__lesson--soon" data-map-lesson="' . esc_attr( $ds_step ) . '">'
					. sprintf(
						/* translators: %s — ступень: Junior, Middle или Senior. */
						esc_html__( '%s — урок пишется', 'designstack-core' ),
						esc_html( $ds_name )
					) . '</span>';
			}
		}

		$ds_out .= '</div>';
		$ds_out .= '</li>';
	}

	$ds_out .= '</ul></section>';
}

$ds_out .= '</div>';

echo $ds_out; // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — разметка собрана выше с экранированием каждой части.

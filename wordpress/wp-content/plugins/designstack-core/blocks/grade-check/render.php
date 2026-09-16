<?php
/**
 * Разметка блока «Проверка грейда».
 *
 * Вопросы рисуются на сервере: страница остаётся читаемой без скриптов и попадает в поиск.
 * Браузер превращает список в пошаговую проверку и считает результат. Грейд варианта лежит
 * в `data-grade` — скрипту он нужен для подсчёта, — но на экране рядом с ответом не показывается:
 * ярлык подсказывает выбор и ломает измерение (D142). Прятать его глубже смысла нет, исходник
 * страницы всё равно открыт, а правило подсчёта мы и так объясняем в результате.
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

$ds_links = designstack_core_skill_resources();
$ds_total = designstack_core_skills_count();
$ds_index = 0;

// Адрес карты развития знает только сервер: результат собирает браузер и сам его не найдёт.
$ds_map = get_page_by_path( 'map' );
$ds_map = ( $ds_map && 'publish' === $ds_map->post_status ) ? (string) get_permalink( $ds_map ) : '';

$ds_out  = '<div class="ds-check" data-check data-total="' . esc_attr( (string) $ds_total ) . '"'
	. ( $ds_map ? ' data-map-url="' . esc_url( $ds_map ) . '"' : '' ) . '>';
$ds_out .= '<div class="ds-check__intro" data-check-intro>';
$ds_out .= '<p class="ds-check__lead">' . sprintf(
	/* translators: %d — число вопросов. */
	esc_html__( '%d вопросов, около 10–15 минут. Регистрация не нужна, ответы сохраняются только в вашем браузере.', 'designstack-core' ),
	(int) $ds_total
) . '</p>';
$ds_out .= '<p>' . esc_html__( 'По результатам вы получите свой профиль навыков, примерный уровень и рекомендации, куда двигаться дальше.', 'designstack-core' ) . '</p>';
$ds_out .= '<div class="ds-check__actions"><button type="button" class="ds-button ds-button--primary ds-button--lg" data-check-start>'
	. esc_html__( 'Проверить свой грейд', 'designstack-core' ) . '</button>'
	. '<span class="ds-check__resume" data-check-resume hidden>' . esc_html__( 'Есть незаконченная попытка — продолжите с того же места', 'designstack-core' ) . '</span></div>';
$ds_out .= '<p class="ds-check__fine">' . esc_html__( 'Грейды в компаниях устроены по-разному, поэтому результат лучше воспринимать как ориентир, а не как окончательную оценку.', 'designstack-core' ) . '</p>';
$ds_out .= '</div>';

$ds_out .= '<noscript><p class="ds-notice ds-notice--info">'
	. esc_html__( 'Без скриптов проверка не посчитает результат, но все вопросы и варианты ответа ниже видны целиком: по ним можно пройтись самостоятельно.', 'designstack-core' )
	. '</p></noscript>';

$ds_out .= '<div class="ds-check__flow" data-check-flow>';
$ds_out .= '<div class="ds-check__bar" data-check-bar hidden><span class="ds-check__bar-fill" data-check-fill></span></div>';
$ds_out .= '<ol class="ds-check__list">';

foreach ( $ds_areas as $ds_area ) {
	foreach ( $ds_area['skills'] as $ds_skill ) {
		$ds_index++;
		$ds_name = 'q-' . $ds_skill['slug'];

		$ds_out .= '<li class="ds-check__item" data-check-q data-skill="' . esc_attr( $ds_skill['slug'] ) . '">';
		$ds_out .= '<fieldset class="ds-check__field">';
		$ds_out .= '<legend class="ds-check__legend">';
		$ds_out .= '<span class="ds-check__step" data-check-step>' . sprintf(
			/* translators: 1 — номер вопроса, 2 — сколько всего. */
			esc_html__( 'Вопрос %1$d из %2$d', 'designstack-core' ),
			(int) $ds_index,
			(int) $ds_total
		) . '</span>';
		$ds_out .= '<span class="ds-check__area">' . esc_html( $ds_area['name'] ) . '</span>';
		$ds_out .= '<span class="ds-check__name">' . esc_html( $ds_skill['name'] ) . '</span>';
		$ds_out .= '</legend>';
		$ds_out .= '<p class="ds-check__hint">' . esc_html( $ds_skill['hint'] ) . '</p>';
		$ds_out .= '<p class="ds-check__ask">' . esc_html__( 'Что из этого ближе всего к вашему опыту?', 'designstack-core' ) . '</p>';
		$ds_out .= '<div class="ds-check__opts">';

		foreach ( $ds_skill['opts'] as $ds_i => $ds_opt ) {
			$ds_id = $ds_name . '-' . (int) $ds_i;

			// Переключатель лежит внутри метки, поэтому атрибут `for` не нужен: он избыточен и невалиден.
			$ds_out .= '<label class="ds-check__opt">';
			$ds_out .= '<input type="radio" id="' . esc_attr( $ds_id ) . '" name="' . esc_attr( $ds_name ) . '"'
				. ' value="' . esc_attr( (string) $ds_i ) . '" data-grade="' . esc_attr( (string) $ds_opt['grade'] ) . '">';
			$ds_out .= '<span>' . esc_html( $ds_opt['text'] ) . '</span>';
			$ds_out .= '</label>';
		}

		$ds_out .= '</div>';

		$ds_links_for = isset( $ds_links[ $ds_skill['slug'] ] ) ? $ds_links[ $ds_skill['slug'] ] : array();

		$ds_out .= '<div class="ds-check__links" data-check-links hidden>';

		if ( $ds_links_for ) {
			$ds_out .= '<ul class="ds-check__links-list">';

			foreach ( $ds_links_for as $ds_link ) {
				$ds_label = designstack_core_skill_type_label( $ds_link['type'] );

				$ds_out .= '<li><a href="' . esc_url( $ds_link['url'] ) . '">' . esc_html( $ds_link['title'] ) . '</a>';
				$ds_out .= $ds_label ? ' <span class="ds-check__kind">' . esc_html( $ds_label ) . '</span>' : '';
				$ds_out .= '</li>';
			}

			$ds_out .= '</ul>';
		} else {
			$ds_out .= '<p class="ds-check__none">' . esc_html__( 'По этому навыку в каталоге пока ничего нет — материал появится здесь, когда мы его проверим.', 'designstack-core' ) . '</p>';
		}

		$ds_out .= '</div>';
		$ds_out .= '</fieldset>';
		$ds_out .= '<div class="ds-check__nav" data-check-nav hidden>';
		$ds_out .= '<button type="button" class="ds-button ds-button--primary" data-check-next>' . esc_html__( 'Дальше', 'designstack-core' ) . '</button>';
		$ds_out .= '<button type="button" class="ds-button ds-button--secondary" data-check-back>' . esc_html__( 'Назад', 'designstack-core' ) . '</button>';
		$ds_out .= '</div>';
		$ds_out .= '</li>';
	}
}

$ds_out .= '</ol></div>';

$ds_out .= '<div class="ds-check__result" data-check-result hidden tabindex="-1"></div>';
$ds_out .= '</div>';

echo $ds_out; // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — разметка собрана выше с экранированием каждой части.

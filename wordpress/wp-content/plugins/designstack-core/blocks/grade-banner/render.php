<?php
/**
 * Разметка блока «Баннер проверки грейда».
 *
 * Раскладка Б (D147): текст и кнопка лежат поверх фото, читаемость держит затемнение
 * `surface-scrim`. Пока фото не загружено, затемнение работает сплошной подложкой — блок
 * не ждёт картинку, чтобы начать работать, и не рисует пустую рамку.
 *
 * Блока нет, пока нет страницы проверки: обещание без работающей страницы — битая ссылка.
 * То же правило у блока подписки, когда не заведён телеграм-канал.
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_page = get_page_by_path( 'grade-check' );

if ( ! $ds_page || 'publish' !== $ds_page->post_status ) {
	return;
}

$ds_photo = (int) get_option( 'designstack_core_banner_photo', 0 );
$ds_image = '';

if ( $ds_photo && wp_attachment_is_image( $ds_photo ) ) {
	$ds_image = wp_get_attachment_image(
		$ds_photo,
		'full',
		false,
		array(
			'class'    => 'ds-banner__photo',
			'loading'  => 'eager',
			'decoding' => 'async',
		)
	);
}

$ds_square = (int) get_option( 'designstack_core_banner_photo_square', 0 );

if ( $ds_image && $ds_square && wp_attachment_is_image( $ds_square ) ) {
	$ds_image = sprintf(
		'<picture><source media="(max-width: 47.9375rem)" srcset="%s">%s</picture>',
		esc_url( (string) wp_get_attachment_image_url( $ds_square, 'full' ) ),
		$ds_image
	);
}

// Карта развития — второй адрес баннера: кто проверку уже прошёл, тому нужна она,
// а не тест сначала. Подставляет скрипт: ответы лежат в браузере, сервер их не видит.
$ds_map = get_page_by_path( 'map' );
$ds_map = ( $ds_map && 'publish' === $ds_map->post_status ) ? (string) get_permalink( $ds_map ) : '';

$ds_out  = '<section class="ds-banner' . ( $ds_image ? ' ds-banner--photo' : '' ) . '"'
	. ' data-banner'
	. ' data-banner-total="' . esc_attr( (string) designstack_core_skills_count() ) . '"'
	. ( $ds_map ? ' data-banner-map="' . esc_url( $ds_map ) . '"' : '' ) . '>';
$ds_out .= $ds_image;
$ds_out .= '<div class="ds-banner__scrim"></div>';
$ds_out .= '<div class="ds-banner__text">';
$ds_out .= '<h2 class="ds-banner__title">' . esc_html__( 'Карта компетенций', 'designstack-core' ) . '</h2>';
$ds_out .= '<p class="ds-banner__lead" data-banner-lead>'
	. esc_html__( 'Вопросы о сделанной работе, а не самооценка по шкале. На выходе — профиль навыков и план, что учить дальше.', 'designstack-core' ) . '</p>';
$ds_out .= '<a class="ds-button ds-button--onscrim ds-button--lg" href="' . esc_url( (string) get_permalink( $ds_page ) ) . '"'
	. ' data-banner-action data-track="grade-check" data-track-source="home">'
	. esc_html__( 'Проверить грейд', 'designstack-core' ) . '</a>';

// Вторая ссылка появляется только у того, кто проверку уже прошёл: её показывает скрипт.
$ds_out .= '<p class="ds-banner__again" data-banner-again hidden></p>';
$ds_out .= '</div></section>';

echo $ds_out; // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — разметка собрана выше с экранированием каждой части.

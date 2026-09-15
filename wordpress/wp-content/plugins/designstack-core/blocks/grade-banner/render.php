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
			'class'    => 'ds-hero__photo',
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

$ds_out  = '<section class="ds-hero' . ( $ds_image ? ' ds-hero--photo' : '' ) . '">';
$ds_out .= $ds_image;
$ds_out .= '<div class="ds-hero__scrim"></div>';
$ds_out .= '<div class="ds-hero__text">';
$ds_out .= '<h2 class="ds-hero__title">' . esc_html__( 'Карта компетенций', 'designstack-core' ) . '</h2>';
$ds_out .= '<p class="ds-hero__lead">' . esc_html__( 'Вопросы о сделанной работе, а не самооценка по шкале. На выходе — профиль навыков и план, что учить дальше.', 'designstack-core' ) . '</p>';
$ds_out .= '<a class="ds-button ds-button--onscrim ds-button--lg" href="' . esc_url( (string) get_permalink( $ds_page ) ) . '" data-track="grade-check" data-track-source="home">'
	. esc_html__( 'Проверить грейд', 'designstack-core' ) . '</a>';
$ds_out .= '</div></section>';

echo $ds_out; // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — разметка собрана выше с экранированием каждой части.

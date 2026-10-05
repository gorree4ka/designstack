<?php
/**
 * Разметка блока «Новые уроки» на главной (D197).
 *
 * Три последних по дате публикации урока и ссылка на страницу всех уроков. Блок обновляется
 * сам с каждым новым уроком. Заголовок карточки — h3: секция главной открывается h2.
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_lessons = get_posts(
	array(
		'post_type'      => 'lesson',
		'post_status'    => 'publish',
		'posts_per_page' => 3,
		'orderby'        => array(
			'date' => 'DESC',
			'ID'   => 'DESC',
		),
	)
);

if ( ! $ds_lessons ) {
	return;
}

$ds_ready = 0;

foreach ( designstack_core_lessons_index() as $ds_steps ) {
	$ds_ready += count( $ds_steps );
}

$ds_cards = '';

foreach ( $ds_lessons as $ds_lesson ) {
	$ds_cards .= '<article class="ds-lessons__card">'
		. '<p class="ds-lessons__step">' . esc_html( designstack_core_lesson_label( $ds_lesson->ID ) ) . '</p>'
		. '<h3 class="ds-lessons__card-title"><a class="ds-lessons__link" href="' . esc_url( (string) get_permalink( $ds_lesson ) ) . '">'
		. esc_html( get_the_title( $ds_lesson ) ) . '</a></h3></article>';
}

echo designstack_core_section( // phpcs:ignore WordPress.Security.EscapingOutput.OutputNotEscaped — секция экранирует заголовки, карточки собраны выше.
	__( 'Новые уроки', 'designstack-core' ),
	__( 'Уроки по навыкам карты развития: тренажёры, задание и чек-лист. Бесплатно.', 'designstack-core' ),
	'<div class="ds-lessons__cards">' . $ds_cards . '</div>',
	designstack_core_more_link(
		(string) get_post_type_archive_link( 'lesson' ),
		sprintf(
			/* translators: %s — «54 урока». */
			__( 'Все %s', 'designstack-core' ),
			designstack_core_lessons_count_line( $ds_ready )
		)
	)
);

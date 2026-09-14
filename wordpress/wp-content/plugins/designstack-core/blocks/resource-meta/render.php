<?php
/**
 * Разметка блока «Факты о ресурсе».
 *
 * Порядок подписей — docs/VOICE.md, раздел «Страница ресурса»: сначала общие
 * факты, потом поля своего типа. Пустое поле строки не занимает.
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

$ds_only   = array_map( 'sanitize_key', (array) ( $attributes['fields'] ?? array() ) );
$ds_type   = designstack_core_get_type( $ds_post_id );
$ds_fields = designstack_core_fields_for_type( $ds_type );
$ds_rows   = array();

// Общие факты идут в порядке словаря, а не реестра полей.
$ds_common = array( 'pricing', 'ru_open', 'ru_payment', 'language' );

foreach ( $ds_common as $ds_key ) {
	if ( $ds_only && ! in_array( $ds_key, $ds_only, true ) ) {
		continue;
	}

	$ds_value = designstack_core_field_value( $ds_post_id, $ds_key );

	if ( ! $ds_value ) {
		continue;
	}

	$ds_note = '';

	if ( 'pricing' === $ds_key ) {
		$ds_price_note = designstack_core_get_field( $ds_post_id, 'price_note' );
		$ds_note       = $ds_price_note ? '<span class="ds-facts__note">' . esc_html( $ds_price_note ) . '</span>' : '';
	}

	if ( in_array( $ds_key, array( 'ru_open', 'ru_payment' ), true ) ) {
		$ds_hint = designstack_core_status_hint( $ds_key, (string) designstack_core_get_field( $ds_post_id, $ds_key ) );
		$ds_note = $ds_hint ? '<span class="ds-facts__note">' . esc_html( $ds_hint ) . '</span>' : '';
	}

	$ds_rows[] = array( $ds_fields[ $ds_key ]['label'], $ds_value . $ds_note );
}

// Грейд и темы — таксономии, а не поля.
$ds_levels = get_the_terms( $ds_post_id, 'level' );

if ( $ds_levels && ! is_wp_error( $ds_levels ) ) {
	$ds_rows[] = array(
		__( 'Грейд', 'designstack-core' ),
		esc_html( designstack_core_join( wp_list_pluck( $ds_levels, 'name' ) ) ),
	);
}

if ( ! empty( $attributes['showTopics'] ) ) {
	$ds_topics = get_the_terms( $ds_post_id, 'topic' );

	if ( $ds_topics && ! is_wp_error( $ds_topics ) ) {
		$ds_links = array();

		foreach ( $ds_topics as $ds_topic ) {
			$ds_links[] = sprintf(
				'<a class="ds-link" href="%1$s">%2$s</a>',
				esc_url( (string) get_term_link( $ds_topic ) ),
				esc_html( $ds_topic->name )
			);
		}

		// Значение факта — flex-колонка, поэтому каждый инлайновый ребёнок встаёт на свою строку
		// и разделитель «·» повисает отдельно. Список ссылок отдаём одним элементом.
		$ds_rows[] = array(
			__( 'Темы', 'designstack-core' ),
			sprintf( '<span class="ds-facts__inline">%s</span>', designstack_core_join( $ds_links ) ),
		);
	}
}

// Поля своего типа.
foreach ( $ds_fields as $ds_key => $ds_field ) {
	if ( 'common' === $ds_field['group'] || 'terms' === $ds_field['control'] ) {
		continue;
	}

	if ( $ds_only && ! in_array( $ds_key, $ds_only, true ) ) {
		continue;
	}

	$ds_value = designstack_core_field_value( $ds_post_id, $ds_key );

	if ( '' === $ds_value ) {
		continue;
	}

	$ds_rows[] = array( $ds_field['label'], $ds_value );
}

if ( ! $ds_rows ) {
	return;
}

$ds_list = '';

foreach ( $ds_rows as $ds_row ) {
	$ds_list .= sprintf(
		'<dt class="ds-facts__label">%1$s</dt><dd class="ds-facts__value">%2$s</dd>',
		esc_html( $ds_row[0] ),
		$ds_row[1]
	);
}

$ds_wrapper = get_block_wrapper_attributes( array( 'class' => 'ds-facts' ) );

// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- значения экранированы при сборке, kses вырезал бы svg меток.
printf(
	'<aside %1$s aria-label="%2$s"><dl class="ds-facts__list">%3$s</dl></aside>',
	$ds_wrapper,
	esc_attr__( 'Факты о ресурсе', 'designstack-core' ),
	$ds_list
);

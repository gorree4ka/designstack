<?php
/**
 * Grey-box stubs for directive 08: batch 1 «Каталог», batch 2 «Главная», batch 3 «Редакция», batch 4 «Форма».
 *
 * Run: tools/wp.cmd --path=wordpress eval-file scripts/greybox-stubs.php
 * Idempotent: an existing entry with the same path and post type is updated, not duplicated.
 * Stubs carry meta _designstack_stub=1, so stage 13 removes them in one command.
 * Pages get a theme template. Batch 3 stubs are posts, as collections and digest issues are in production:
 * the collection renders with single.html by the template hierarchy, states use post templates from customTemplates.
 * Batch 4: /suggest/ and its child /suggest/thanks/ are real pages at their real URLs (page-suggest.html and page.html
 * by the template hierarchy), so they get no stub meta and stage 13 keeps them; the form states are stubs.
 *
 * @package designstack
 */

if ( ! defined( 'WP_CLI' ) ) {
	exit;
}

// Slug, title, template ('' — by the template hierarchy), post type, parent slug, stub.
$designstack_stubs = array(
	array( 'tools', 'Инструменты', 'taxonomy-resource_type', 'page', '', true ),
	array( 'tools-empty', 'Инструменты: пустая выдача', 'greybox-tools-empty', 'page', '', true ),
	array( 'resource-figma', 'Figma', 'single-resource', 'page', '', true ),
	array( 'resource-invision', 'InVision', 'greybox-resource-closed', 'page', '', true ),
	array( 'resource-laws-of-ux', 'Laws of UX', 'greybox-resource-learning', 'page', '', true ),
	array( 'topic-prototyping', 'Прототипирование', 'taxonomy-topic', 'page', '', true ),
	array( 'topic-prototyping-community', 'Прототипирование: сообществ нет', 'greybox-topic-empty', 'page', '', true ),
	array( 'home-empty', 'Главная: нет свежих проверок и канала', 'greybox-home-empty', 'page', '', true ),
	array( 'collections-free-prototyping', 'Бесплатный набор для прототипирования', '', 'post', '', true ),
	array( 'collections-free-prototyping-empty', 'Бесплатный набор для прототипирования: ресурсов не осталось', 'greybox-collection-empty', 'post', '', true ),
	array( 'digest-2026-36', 'Дайджест за 31 авг — 6 сен 2026', 'greybox-digest-issue', 'post', '', true ),
	array( 'digest-2026-35', 'Дайджест за 24–30 авг 2026', 'greybox-digest-issue-older', 'post', '', true ),
	array( 'suggest', 'Предложить ресурс', '', 'page', '', false ),
	array( 'thanks', 'Спасибо', '', 'page', 'suggest', false ),
	array( 'suggest-errors', 'Предложить ресурс: ошибки полей', 'greybox-suggest-errors', 'page', '', true ),
	array( 'suggest-sending', 'Предложить ресурс: отправка', 'greybox-suggest-sending', 'page', '', true ),
	array( 'suggest-failed', 'Предложить ресурс: ошибка отправки', 'greybox-suggest-failed', 'page', '', true ),
	array( 'suggest-limit', 'Предложить ресурс: лимит отправок', 'greybox-suggest-limit', 'page', '', true ),
	array( 'suggest-duplicate', 'Предложить ресурс: ресурс уже есть в каталоге', 'greybox-suggest-duplicate', 'page', '', true ),
);

foreach ( $designstack_stubs as $designstack_stub ) {
	list( $slug, $title, $template, $type, $parent_slug, $is_stub ) = $designstack_stub;

	$parent_id = 0;
	$path      = $slug;
	if ( '' !== $parent_slug ) {
		$parent = get_page_by_path( $parent_slug, OBJECT, $type );
		if ( ! $parent ) {
			WP_CLI::error( $slug . ': parent ' . $parent_slug . ' not found' );
		}
		$parent_id = $parent->ID;
		$path      = $parent_slug . '/' . $slug;
	}

	$args = array(
		'post_type'    => $type,
		'post_status'  => 'publish',
		'post_title'   => $title,
		'post_name'    => $slug,
		'post_parent'  => $parent_id,
		'post_content' => '',
	);
	if ( $is_stub ) {
		$args['meta_input'] = array( '_designstack_stub' => '1' );
	}
	if ( '' !== $template ) {
		$args['page_template'] = $template;
	}

	$existing = get_page_by_path( $path, OBJECT, $type );
	if ( $existing ) {
		$args['ID'] = $existing->ID;
		$id         = wp_update_post( $args, true );
	} else {
		$id = wp_insert_post( $args, true );
	}

	if ( is_wp_error( $id ) ) {
		WP_CLI::error( $path . ': ' . $id->get_error_message() );
	}
	if ( ! $is_stub ) {
		delete_post_meta( $id, '_designstack_stub' );
	}

	$assigned = get_page_template_slug( $id );
	if ( '' === $assigned ) {
		$assigned = '(по иерархии шаблонов)';
	}
	WP_CLI::log( sprintf( '%-36s %-4s ID %-4d %-5s template %s', $path, $type, $id, $is_stub ? 'stub' : 'page', $assigned ) );
}

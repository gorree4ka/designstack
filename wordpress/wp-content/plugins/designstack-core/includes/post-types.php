<?php
/**
 * Тип записи «Ресурс».
 *
 * Один тип на все четыре вида каталога, вид задаёт таксономия resource_type (D59).
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Регистрирует тип записи resource.
 *
 * Общего архива нет (D30): /resource/ отвечает 404, страница ресурса живёт
 * на /resource/{slug}/, списки собираются архивами таксономий.
 *
 * @return void
 */
function designstack_core_register_post_type(): void {
	$labels = array(
		'name'                  => __( 'Ресурсы', 'designstack-core' ),
		'singular_name'         => __( 'Ресурс', 'designstack-core' ),
		'menu_name'             => __( 'Ресурсы', 'designstack-core' ),
		'add_new'               => __( 'Добавить ресурс', 'designstack-core' ),
		'add_new_item'          => __( 'Добавить ресурс', 'designstack-core' ),
		'edit_item'             => __( 'Изменить ресурс', 'designstack-core' ),
		'new_item'              => __( 'Новый ресурс', 'designstack-core' ),
		'view_item'             => __( 'Открыть ресурс', 'designstack-core' ),
		'view_items'            => __( 'Открыть ресурсы', 'designstack-core' ),
		'search_items'          => __( 'Искать ресурсы', 'designstack-core' ),
		'not_found'             => __( 'Ресурсов нет', 'designstack-core' ),
		'not_found_in_trash'    => __( 'В корзине ресурсов нет', 'designstack-core' ),
		'all_items'             => __( 'Все ресурсы', 'designstack-core' ),
		'archives'              => __( 'Ресурсы', 'designstack-core' ),
		'insert_into_item'      => __( 'Вставить в ресурс', 'designstack-core' ),
		'uploaded_to_this_item' => __( 'Загружено к ресурсу', 'designstack-core' ),
		'featured_image'        => __( 'Логотип ресурса', 'designstack-core' ),
		'set_featured_image'    => __( 'Выбрать логотип', 'designstack-core' ),
		'remove_featured_image' => __( 'Убрать логотип', 'designstack-core' ),
		'use_featured_image'    => __( 'Сделать логотипом', 'designstack-core' ),
		'item_published'        => __( 'Ресурс опубликован', 'designstack-core' ),
		'item_updated'          => __( 'Ресурс обновлён', 'designstack-core' ),
		'item_scheduled'        => __( 'Публикация ресурса запланирована', 'designstack-core' ),
		'item_reverted_to_draft' => __( 'Ресурс вернулся в черновики', 'designstack-core' ),
	);

	register_post_type(
		'resource',
		array(
			'labels'             => $labels,
			'description'        => __( 'Запись каталога: инструмент, учебный материал, ассет или сообщество.', 'designstack-core' ),
			'public'             => true,
			'publicly_queryable' => true,
			'show_ui'            => true,
			'show_in_menu'       => true,
			'show_in_nav_menus'  => true,
			'show_in_rest'       => true,
			'rest_base'          => 'resource',
			'menu_position'      => 5,
			'menu_icon'          => 'dashicons-screenoptions',
			'capability_type'    => 'post',
			'map_meta_cap'       => true,
			'hierarchical'       => false,
			'has_archive'        => false,
			'rewrite'            => array(
				'slug'       => 'resource',
				'with_front' => false,
				'feeds'      => false,
			),
			'query_var'          => true,
			'supports'           => array( 'title', 'editor', 'thumbnail', 'excerpt', 'author', 'revisions', 'custom-fields' ),
			'taxonomies'         => array( 'resource_type', 'topic', 'level', 'skill' ),
			'delete_with_user'   => false,
		)
	);
}
add_action( 'init', 'designstack_core_register_post_type', 0 );

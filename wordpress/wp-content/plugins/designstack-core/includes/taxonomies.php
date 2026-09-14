<?php
/**
 * Таксономии каталога: тип, тема, грейд, навык.
 *
 * Адреса разделов /tools/, /learn/, /assets/, /community/ делает includes/rewrite.php:
 * штатный архив таксономии остаётся запасным адресом и отвечает 301.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Словарь термов, создаваемых при активации: таксономия → слаг → название.
 *
 * @return array<string, array<string, string>>
 */
function designstack_core_terms(): array {
	return array(
		'resource_type' => array(
			'tool'      => __( 'Инструмент', 'designstack-core' ),
			'learning'  => __( 'Учебный материал', 'designstack-core' ),
			'asset'     => __( 'Ассет', 'designstack-core' ),
			'community' => __( 'Сообщество', 'designstack-core' ),
		),
		'topic'         => array(
			'ux-research'         => __( 'UX-исследования', 'designstack-core' ),
			'prototyping'         => __( 'Прототипирование', 'designstack-core' ),
			'ui-visual'           => __( 'UI и визуал', 'designstack-core' ),
			'typography'          => __( 'Типографика', 'designstack-core' ),
			'icons-illustrations' => __( 'Иконки и иллюстрации', 'designstack-core' ),
			'design-systems'      => __( 'Дизайн-системы', 'designstack-core' ),
			'ai-for-designers'    => __( 'AI для дизайнера', 'designstack-core' ),
			'analytics-metrics'   => __( 'Аналитика и метрики', 'designstack-core' ),
			'career-portfolio'    => __( 'Карьера и портфолио', 'designstack-core' ),
			'accessibility'       => __( 'Доступность', 'designstack-core' ),
			'mobile-design'       => __( 'Мобильный дизайн', 'designstack-core' ),
			'web-landings'        => __( 'Веб и лендинги', 'designstack-core' ),
		),
		'level'         => array(
			'junior' => __( 'Junior', 'designstack-core' ),
			'middle' => __( 'Middle', 'designstack-core' ),
			'senior' => __( 'Senior', 'designstack-core' ),
		),
	);
}

/**
 * Регистрирует таксономии ресурса.
 *
 * @return void
 */
function designstack_core_register_taxonomies(): void {
	register_taxonomy(
		'resource_type',
		array( 'resource' ),
		array(
			'labels'            => array(
				'name'          => __( 'Типы', 'designstack-core' ),
				'singular_name' => __( 'Тип', 'designstack-core' ),
				'menu_name'     => __( 'Типы', 'designstack-core' ),
				'all_items'     => __( 'Все типы', 'designstack-core' ),
				'edit_item'     => __( 'Изменить тип', 'designstack-core' ),
				'add_new_item'  => __( 'Добавить тип', 'designstack-core' ),
				'search_items'  => __( 'Искать типы', 'designstack-core' ),
				'not_found'     => __( 'Типов нет', 'designstack-core' ),
			),
			'description'       => __( 'Вид ресурса: инструмент, учебный материал, ассет, сообщество.', 'designstack-core' ),
			'public'            => true,
			'hierarchical'      => false,
			'show_ui'           => true,
			'show_in_rest'      => true,
			'show_admin_column' => true,
			'show_in_nav_menus' => true,
			'meta_box_cb'       => 'designstack_core_resource_type_meta_box',
			'rewrite'           => array(
				'slug'       => 'resource_type',
				'with_front' => false,
			),
			'query_var'         => 'resource_type',
		)
	);

	register_taxonomy(
		'topic',
		array( 'resource' ),
		array(
			'labels'            => array(
				'name'          => __( 'Темы', 'designstack-core' ),
				'singular_name' => __( 'Тема', 'designstack-core' ),
				'menu_name'     => __( 'Темы', 'designstack-core' ),
				'all_items'     => __( 'Все темы', 'designstack-core' ),
				'parent_item'   => __( 'Родительская тема', 'designstack-core' ),
				'edit_item'     => __( 'Изменить тему', 'designstack-core' ),
				'add_new_item'  => __( 'Добавить тему', 'designstack-core' ),
				'search_items'  => __( 'Искать темы', 'designstack-core' ),
				'not_found'     => __( 'Тем нет', 'designstack-core' ),
			),
			'public'            => true,
			'hierarchical'      => true,
			'show_ui'           => true,
			'show_in_rest'      => true,
			'show_admin_column' => true,
			'show_in_nav_menus' => true,
			'rewrite'           => array(
				'slug'         => 'topic',
				'with_front'   => false,
				'hierarchical' => false,
			),
			'query_var'         => 'topic',
		)
	);

	// Грейд и навык — без публичных архивов: грейд работает параметром фильтра
	// в разделах, навык виден только в редакторе и REST (карта URL, этап 07).
	register_taxonomy(
		'level',
		array( 'resource' ),
		array(
			'labels'            => array(
				'name'          => __( 'Грейды', 'designstack-core' ),
				'singular_name' => __( 'Грейд', 'designstack-core' ),
				'menu_name'     => __( 'Грейды', 'designstack-core' ),
				'all_items'     => __( 'Все грейды', 'designstack-core' ),
				'edit_item'     => __( 'Изменить грейд', 'designstack-core' ),
				'add_new_item'  => __( 'Добавить грейд', 'designstack-core' ),
				'search_items'  => __( 'Искать грейды', 'designstack-core' ),
				'not_found'     => __( 'Грейдов нет', 'designstack-core' ),
			),
			'description'       => __( 'Для кого ресурс: junior, middle, senior.', 'designstack-core' ),
			'public'            => false,
			'publicly_queryable' => false,
			'hierarchical'      => false,
			'show_ui'           => true,
			'show_in_rest'      => true,
			'show_admin_column' => true,
			'show_in_nav_menus' => false,
			'rewrite'           => false,
			'query_var'         => false,
		)
	);

	register_taxonomy(
		'skill',
		array( 'resource' ),
		array(
			'labels'            => array(
				'name'          => __( 'Навыки', 'designstack-core' ),
				'singular_name' => __( 'Навык', 'designstack-core' ),
				'menu_name'     => __( 'Навыки', 'designstack-core' ),
				'all_items'     => __( 'Все навыки', 'designstack-core' ),
				'parent_item'   => __( 'Область навыка', 'designstack-core' ),
				'edit_item'     => __( 'Изменить навык', 'designstack-core' ),
				'add_new_item'  => __( 'Добавить навык', 'designstack-core' ),
				'search_items'  => __( 'Искать навыки', 'designstack-core' ),
				'not_found'     => __( 'Навыков нет', 'designstack-core' ),
			),
			'description'       => __( 'Навык нашей карты компетенций: область → навык (D22, D26).', 'designstack-core' ),
			'public'            => false,
			'publicly_queryable' => false,
			'hierarchical'      => true,
			'show_ui'           => true,
			'show_in_rest'      => true,
			'show_admin_column' => false,
			'show_in_nav_menus' => false,
			'rewrite'           => false,
			'query_var'         => false,
		)
	);
}
add_action( 'init', 'designstack_core_register_taxonomies', 1 );

/**
 * Панель типа в редакторе: радиокнопки вместо флажков — тип ровно один.
 *
 * @param WP_Post $post     Запись.
 * @param array   $box_args Аргументы метабокса.
 * @return void
 */
function designstack_core_resource_type_meta_box( $post, $box_args = array() ): void {
	$taxonomy = $box_args['args']['taxonomy'] ?? 'resource_type';
	$terms    = get_terms(
		array(
			'taxonomy'   => $taxonomy,
			'hide_empty' => false,
			'orderby'    => 'term_id',
		)
	);

	if ( is_wp_error( $terms ) ) {
		return;
	}

	$current = wp_get_object_terms( (int) $post->ID, $taxonomy, array( 'fields' => 'slugs' ) );
	$current = is_wp_error( $current ) ? array() : $current;
	$current = $current[0] ?? '';

	echo '<div class="ds-core-type">';
	wp_nonce_field( 'designstack_core_type', 'designstack_core_type_nonce' );
	echo '<p class="description">' . esc_html__( 'Тип ровно один: он задаёт поля ниже и раздел сайта.', 'designstack-core' ) . '</p>';
	echo '<ul class="categorychecklist form-no-clear">';

	foreach ( $terms as $term ) {
		printf(
			'<li><label class="selectit"><input type="radio" name="designstack_core_resource_type" value="%1$s"%2$s> %3$s</label></li>',
			esc_attr( $term->slug ),
			checked( $current, $term->slug, false ),
			esc_html( $term->name )
		);
	}

	echo '</ul></div>';
}

/**
 * Сохраняет выбранный тип и следит, чтобы он остался один.
 *
 * @param int $post_id Идентификатор записи.
 * @return void
 */
function designstack_core_save_resource_type( int $post_id ): void {
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}

	$nonce = isset( $_POST['designstack_core_type_nonce'] )
		? sanitize_text_field( wp_unslash( $_POST['designstack_core_type_nonce'] ) )
		: '';

	if ( $nonce && wp_verify_nonce( $nonce, 'designstack_core_type' ) && current_user_can( 'edit_post', $post_id ) ) {
		$slug  = isset( $_POST['designstack_core_resource_type'] )
			? sanitize_key( wp_unslash( $_POST['designstack_core_resource_type'] ) )
			: '';
		$terms = designstack_core_terms()['resource_type'];

		if ( isset( $terms[ $slug ] ) ) {
			wp_set_object_terms( $post_id, $slug, 'resource_type', false );
		}
	}

	// Тип один и тогда, когда запись пришла из REST или WP-CLI: лишние термы снимаем.
	$assigned = wp_get_object_terms( $post_id, 'resource_type', array( 'fields' => 'slugs' ) );

	if ( ! is_wp_error( $assigned ) && count( $assigned ) > 1 ) {
		wp_set_object_terms( $post_id, $assigned[0], 'resource_type', false );
	}
}
add_action( 'save_post_resource', 'designstack_core_save_resource_type', 20 );

/**
 * Создаёт термы словаря, которых ещё нет. Вызывается при активации.
 *
 * @return array<string, int> Сколько термов создано в каждой таксономии.
 */
function designstack_core_install_terms(): array {
	$created = array();

	foreach ( designstack_core_terms() as $taxonomy => $terms ) {
		$created[ $taxonomy ] = 0;

		foreach ( $terms as $slug => $name ) {
			if ( term_exists( $slug, $taxonomy ) ) {
				continue;
			}

			$result = wp_insert_term( $name, $taxonomy, array( 'slug' => $slug ) );

			if ( ! is_wp_error( $result ) ) {
				++$created[ $taxonomy ];
			}
		}
	}

	return $created;
}

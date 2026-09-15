<?php
/**
 * Тип записи «Урок» — уроки карты компетенций.
 *
 * Урок поднимает человека на одну ступень по одному навыку: 37 навыков × 3 ступени.
 * Критерий приёмки урока — вариант ответа из карты (`docs/skills-map/lessons.md`).
 *
 * Адрес плоский: `/lessons/{slug}/`, где slug — `навык-ступень`. Двухуровневый адрес
 * вида `/lessons/навык/ступень/` требует своего правила перезаписи и ломается на
 * пересечениях с архивами; выигрыш только в красоте адреса (D152).
 * Корень `/learn/` занят каталогом «Учёба» — это чужие материалы, а не наши уроки.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Регистрирует тип записи lesson.
 *
 * Общего архива нет: список уроков живёт на карте развития `/map/`, а не отдельной лентой.
 *
 * @return void
 */
function designstack_core_register_lesson(): void {
	$labels = array(
		'name'               => __( 'Уроки', 'designstack-core' ),
		'singular_name'      => __( 'Урок', 'designstack-core' ),
		'menu_name'          => __( 'Уроки', 'designstack-core' ),
		'add_new'            => __( 'Добавить урок', 'designstack-core' ),
		'add_new_item'       => __( 'Добавить урок', 'designstack-core' ),
		'edit_item'          => __( 'Изменить урок', 'designstack-core' ),
		'new_item'           => __( 'Новый урок', 'designstack-core' ),
		'view_item'          => __( 'Открыть урок', 'designstack-core' ),
		'search_items'       => __( 'Искать уроки', 'designstack-core' ),
		'not_found'          => __( 'Уроков нет', 'designstack-core' ),
		'not_found_in_trash' => __( 'В корзине уроков нет', 'designstack-core' ),
		'all_items'          => __( 'Все уроки', 'designstack-core' ),
	);

	register_post_type(
		'lesson',
		array(
			'labels'             => $labels,
			'description'        => __( 'Урок карты компетенций: один навык, одна ступень.', 'designstack-core' ),
			'public'             => true,
			'publicly_queryable' => true,
			'show_ui'            => true,
			'show_in_menu'       => true,
			'show_in_nav_menus'  => false,
			'show_in_rest'       => true,
			'rest_base'          => 'lesson',
			'menu_position'      => 6,
			'menu_icon'          => 'dashicons-welcome-learn-more',
			'capability_type'    => 'post',
			'map_meta_cap'       => true,
			'hierarchical'       => false,
			'has_archive'        => false,
			'rewrite'            => array(
				'slug'       => 'lessons',
				'with_front' => false,
				'feeds'      => false,
			),
			'query_var'          => true,
			'supports'           => array( 'title', 'editor', 'excerpt', 'revisions', 'custom-fields' ),
			'taxonomies'         => array( 'skill' ),
			'delete_with_user'   => false,
		)
	);

	// Ступень хранится отдельным полем: по ней карта выбирает, какой урок показать.
	register_post_meta(
		'lesson',
		'lesson_step',
		array(
			'type'              => 'string',
			'single'            => true,
			'show_in_rest'      => true,
			'sanitize_callback' => 'designstack_core_sanitize_step',
			'auth_callback'     => function () {
				return current_user_can( 'edit_posts' );
			},
		)
	);
}
add_action( 'init', 'designstack_core_register_lesson', 0 );

/**
 * Приводит ступень к одному из трёх значений карты.
 *
 * @param mixed $value Введённое значение.
 * @return string Ступень или пустая строка.
 */
function designstack_core_sanitize_step( $value ): string {
	$value = is_string( $value ) ? strtolower( trim( $value ) ) : '';

	return in_array( $value, array( 'junior', 'middle', 'senior' ), true ) ? $value : '';
}

/**
 * Карта опубликованных уроков: слаг навыка → ступень → адрес.
 *
 * Одним запросом на всю страницу: карта развития спрашивает про 111 клеток сразу,
 * и запрос на каждую превратил бы её в сотню обращений к базе.
 *
 * @return array<string, array<string, string>>
 */
function designstack_core_lessons_map(): array {
	static $map = null;

	if ( null !== $map ) {
		return $map;
	}

	$map     = array();
	$lessons = get_posts(
		array(
			'post_type'      => 'lesson',
			'post_status'    => 'publish',
			'posts_per_page' => -1,
			'orderby'        => 'ID',
			'order'          => 'ASC',
		)
	);

	foreach ( $lessons as $lesson ) {
		$step = (string) get_post_meta( $lesson->ID, 'lesson_step', true );

		if ( ! $step ) {
			continue;
		}

		$terms = wp_get_post_terms( $lesson->ID, 'skill', array( 'fields' => 'slugs' ) );

		if ( is_wp_error( $terms ) ) {
			continue;
		}

		foreach ( $terms as $slug ) {
			// Навык может быть областью — у неё уроков не бывает, но проверять дешевле, чем ловить потом.
			if ( ! isset( $map[ $slug ] ) ) {
				$map[ $slug ] = array();
			}

			$map[ $slug ][ $step ] = (string) get_permalink( $lesson );
		}
	}

	return $map;
}

/**
 * Русское название ступени для интерфейса.
 *
 * @param string $step Ступень.
 * @return string Подпись.
 */
function designstack_core_step_label( string $step ): string {
	$names = array(
		'junior' => 'Junior',
		'middle' => 'Middle',
		'senior' => 'Senior',
	);

	return isset( $names[ $step ] ) ? $names[ $step ] : '';
}

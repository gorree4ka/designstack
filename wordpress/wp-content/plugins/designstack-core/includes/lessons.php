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
 * Архив `/lessons/` — страница всех уроков по областям и навыкам (D197). Карта развития `/map/`
 * отвечает на другой вопрос — где человек сейчас, — и остаётся отдельной страницей.
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
		// Подпись архива — звено крошек «Главная › Уроки › …» (D197); без неё ядро берёт «Все уроки».
		'archives'           => __( 'Уроки', 'designstack-core' ),
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
			'has_archive'        => 'lessons',
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

	// Короткий заголовок для вкладки и выдачи: форма вопроса, который задают поиску (D197).
	// Длинный заголовок урока читается как фраза и остаётся на странице.
	register_post_meta(
		'lesson',
		'lesson_seo_title',
		array(
			'type'              => 'string',
			'single'            => true,
			'show_in_rest'      => true,
			'sanitize_callback' => 'sanitize_text_field',
			'auth_callback'     => function () {
				return current_user_can( 'edit_posts' );
			},
		)
	);

	// Ресурсы каталога из «Что почитать дальше» — отдельными строками (правило 8 темы):
	// по ним страница ресурса находит уроки, которые его советуют.
	register_post_meta(
		'lesson',
		'lesson_reads',
		array(
			'type'              => 'string',
			'single'            => false,
			'show_in_rest'      => false,
			'sanitize_callback' => 'sanitize_title',
		)
	);
}
add_action( 'init', 'designstack_core_register_lesson', 0 );

/**
 * Список «Что почитать дальше» урока → ресурсы каталога, на которые он ссылается.
 *
 * Пересчитывается при каждом сохранении урока: список живёт в теле урока (его вставляет
 * `scripts/lesson_reads.py`), и отдельное поле разошлось бы с ним после первой правки.
 * Ссылки в остальном тексте урока не считаются — блок на странице ресурса обещает
 * именно рекомендацию после урока.
 *
 * @param int $post_id Урок.
 * @return string[] Слаги ресурсов.
 */
function designstack_core_lesson_reads_sync( int $post_id ): array {
	$post = get_post( $post_id );

	if ( ! $post || 'lesson' !== $post->post_type ) {
		return array();
	}

	$slugs = array();

	if ( preg_match( '#<section[^>]*id="further-reading"[^>]*>(.*?)</section>#s', (string) $post->post_content, $part ) ) {
		preg_match_all( '#href="(?:https?://[^/"]+)?/resource/([a-z0-9-]+)/?"#', $part[1], $found );
		$slugs = array_values( array_unique( $found[1] ) );
	}

	delete_post_meta( $post_id, 'lesson_reads' );

	foreach ( $slugs as $slug ) {
		add_post_meta( $post_id, 'lesson_reads', $slug );
	}

	return $slugs;
}
add_action(
	'save_post_lesson',
	function ( $post_id ) {
		if ( ! wp_is_post_revision( $post_id ) ) {
			designstack_core_lesson_reads_sync( (int) $post_id );
		}
	}
);

/**
 * Все опубликованные уроки: слаг навыка → ступень → название, адрес, дата.
 *
 * Одним запросом на страницу, как `designstack_core_lessons_map()`.
 *
 * @return array<string, array<string, array<string, mixed>>>
 */
function designstack_core_lessons_index(): array {
	static $index = null;

	if ( null !== $index ) {
		return $index;
	}

	$index   = array();
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
		$step  = (string) get_post_meta( $lesson->ID, 'lesson_step', true );
		$terms = wp_get_post_terms( $lesson->ID, 'skill', array( 'fields' => 'slugs' ) );

		if ( ! $step || is_wp_error( $terms ) || ! $terms ) {
			continue;
		}

		$index[ $terms[0] ][ $step ] = array(
			'id'    => $lesson->ID,
			'title' => get_the_title( $lesson ),
			'url'   => (string) get_permalink( $lesson ),
			'date'  => (string) $lesson->post_date,
		);
	}

	return $index;
}

/**
 * Название навыка по слагу — из карты развития.
 *
 * @param string $slug Слаг навыка.
 * @return string
 */
function designstack_core_skill_name( string $slug ): string {
	foreach ( designstack_core_skills_map() as $area ) {
		foreach ( $area['skills'] as $skill ) {
			if ( $slug === $skill['slug'] ) {
				return (string) $skill['name'];
			}
		}
	}

	return '';
}

/**
 * Подпись урока «Навык · Ступень»: крошки, карточки на главной и на странице ресурса.
 *
 * @param int $id Урок.
 * @return string Пустая строка, если у урока нет навыка или ступени.
 */
function designstack_core_lesson_label( int $id ): string {
	$step  = designstack_core_step_label( (string) get_post_meta( $id, 'lesson_step', true ) );
	$terms = wp_get_post_terms( $id, 'skill' );

	if ( ! $step || is_wp_error( $terms ) || ! $terms ) {
		return '';
	}

	return $terms[0]->name . ' · ' . $step;
}

/**
 * Уроки, в чьём «Что почитать дальше» стоит ресурс: по порядку ступеней.
 *
 * @param string $slug Слаг ресурса.
 * @return array<int, array<string, string>>
 */
function designstack_core_lessons_for_resource( string $slug ): array {
	$posts = get_posts(
		array(
			'post_type'      => 'lesson',
			'post_status'    => 'publish',
			'posts_per_page' => -1,
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
				array(
					'key'   => 'lesson_reads',
					'value' => $slug,
				),
			),
		)
	);
	$order = array_flip( array( 'junior', 'middle', 'senior' ) );
	$out   = array();

	foreach ( $posts as $post ) {
		$step  = (string) get_post_meta( $post->ID, 'lesson_step', true );
		$out[] = array(
			'step'  => $step,
			'label' => designstack_core_step_label( $step ),
			'title' => get_the_title( $post ),
			'url'   => (string) get_permalink( $post ),
			'rank'  => ( $order[ $step ] ?? 3 ) . '-' . $post->post_name,
		);
	}

	usort(
		$out,
		function ( $a, $b ) {
			return strcmp( $a['rank'], $b['rank'] );
		}
	);

	return $out;
}

/**
 * У архива уроков одна страница: блок выводит все уроки сам, и `/lessons/page/2/`
 * был бы дублем первой. Основной запрос архива берёт одну запись — она не выводится.
 *
 * @param WP_Query $query Запрос.
 * @return void
 */
function designstack_core_lessons_archive_query( $query ): void {
	if ( $query->is_main_query() && ! is_admin() && $query->is_post_type_archive( 'lesson' ) ) {
		$query->set( 'posts_per_page', 1 );
		$query->set( 'no_found_rows', true );
	}
}
add_action( 'pre_get_posts', 'designstack_core_lessons_archive_query' );

/**
 * Вторая и дальше страница архива уроков — «не найдено».
 *
 * @return void
 */
function designstack_core_lessons_archive_paged(): void {
	if ( is_post_type_archive( 'lesson' ) && is_paged() ) {
		global $wp_query;

		$wp_query->set_404();
		status_header( 404 );
	}
}
add_action( 'template_redirect', 'designstack_core_lessons_archive_paged', 1 );

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

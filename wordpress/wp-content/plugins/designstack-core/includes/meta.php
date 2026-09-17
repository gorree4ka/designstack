<?php
/**
 * Мета-поля ресурса: регистрация, санитизация, доступ.
 *
 * Все поля описаны одним реестром в includes/enums.php — здесь только их регистрация
 * и очистка значений. Поля-списки хранятся отдельными строками meta (D64): по ним
 * работают фильтры, а сериализованный массив запросом не ищется.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Регистрирует мета-поля ресурса.
 *
 * @return void
 */
function designstack_core_register_meta(): void {
	foreach ( designstack_core_fields() as $key => $field ) {
		$multiple = ! empty( $field['multiple'] );

		register_post_meta(
			'resource',
			$key,
			array(
				'single'            => ! $multiple,
				'type'              => $field['type'],
				'description'       => $field['label'],
				'show_in_rest'      => true,
				'sanitize_callback' => static fn( $value ) => designstack_core_sanitize_value( $key, $value ),
				'auth_callback'     => static fn() => current_user_can( 'edit_posts' ),
			)
		);
	}

	// Служебные поля: подчёркивание в начале прячет их из «Произвольных полей» и REST.
	foreach ( array( '_designstack_seed', '_designstack_suggested_by' ) as $key ) {
		register_post_meta(
			'resource',
			$key,
			array(
				'single'            => true,
				'type'              => 'string',
				'show_in_rest'      => false,
				'sanitize_callback' => 'sanitize_text_field',
				'auth_callback'     => static fn() => current_user_can( 'edit_posts' ),
			)
		);
	}
}
add_action( 'init', 'designstack_core_register_meta', 5 );

/**
 * Приводит значение поля к допустимому виду.
 *
 * Чужое значение enum заменяется пустым: врать меткой хуже, чем её не показать.
 *
 * @param string $key   Ключ поля.
 * @param mixed  $value Значение.
 * @return mixed Очищенное значение.
 */
function designstack_core_sanitize_value( string $key, $value ) {
	$fields = designstack_core_fields();

	if ( ! isset( $fields[ $key ] ) ) {
		return '';
	}

	$field = $fields[ $key ];

	if ( isset( $field['enum'] ) ) {
		$allowed = designstack_core_enums()[ $field['enum'] ];
		$value   = is_string( $value ) ? sanitize_key( $value ) : '';

		return isset( $allowed[ $value ] ) ? $value : '';
	}

	switch ( $field['control'] ) {
		case 'url':
			return esc_url_raw( (string) $value );

		case 'textarea':
			return sanitize_textarea_field( (string) $value );

		case 'date':
			$date = DateTimeImmutable::createFromFormat( 'Y-m-d', (string) $value );

			return ( $date && $date->format( 'Y-m-d' ) === (string) $value ) ? (string) $value : '';

		case 'checkbox':
			return rest_sanitize_boolean( $value );

		case 'number':
			return absint( $value );

		case 'posts':
			$id = absint( $value );

			return ( $id && 'resource' === get_post_type( $id ) ) ? $id : 0;

		case 'terms':
			$id = absint( $value );

			return ( $id && term_exists( $id, $field['taxonomy'] ) ) ? $id : 0;

		case 'text':
		default:
			$clean = sanitize_text_field( (string) $value );

			if ( 'file_format' === $key ) {
				$clean = sanitize_key( $clean );
			}

			if ( isset( $field['max'] ) ) {
				$clean = mb_substr( $clean, 0, (int) $field['max'] );
			}

			return $clean;
	}
}

/**
 * Читает поле ресурса с учётом того, список это или одно значение.
 *
 * @param int    $post_id Идентификатор записи.
 * @param string $key     Ключ поля.
 * @return mixed Строка, число, логическое значение или массив значений.
 */
function designstack_core_get_field( int $post_id, string $key ) {
	$fields = designstack_core_fields();

	if ( ! isset( $fields[ $key ] ) ) {
		return '';
	}

	if ( ! empty( $fields[ $key ]['multiple'] ) ) {
		$values = get_post_meta( $post_id, $key, false );

		if ( 'integer' === $fields[ $key ]['type'] ) {
			$values = array_map( 'absint', $values );
		}

		return array_values( array_filter( $values, static fn( $item ) => '' !== $item && 0 !== $item ) );
	}

	$value = get_post_meta( $post_id, $key, true );

	if ( 'boolean' === $fields[ $key ]['type'] ) {
		return (bool) $value;
	}

	if ( 'integer' === $fields[ $key ]['type'] ) {
		return (int) $value;
	}

	return (string) $value;
}

/**
 * Записывает поле ресурса: список — отдельными строками, остальное одним значением.
 *
 * @param int    $post_id Идентификатор записи.
 * @param string $key     Ключ поля.
 * @param mixed  $value   Значение или массив значений.
 * @return void
 */
function designstack_core_set_field( int $post_id, string $key, $value ): void {
	$fields = designstack_core_fields();

	if ( ! isset( $fields[ $key ] ) ) {
		return;
	}

	if ( empty( $fields[ $key ]['multiple'] ) ) {
		update_post_meta( $post_id, $key, designstack_core_sanitize_value( $key, $value ) );

		return;
	}

	delete_post_meta( $post_id, $key );

	foreach ( (array) $value as $item ) {
		$clean = designstack_core_sanitize_value( $key, $item );

		if ( '' === $clean || 0 === $clean ) {
			continue;
		}

		add_post_meta( $post_id, $key, $clean );
	}
}

/**
 * Тип ресурса: слаг терма resource_type или пустая строка.
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_get_type( int $post_id ): string {
	$terms = get_the_terms( $post_id, 'resource_type' );

	if ( ! $terms || is_wp_error( $terms ) ) {
		return '';
	}

	return $terms[0]->slug;
}

/**
 * Поля, которые показываются у ресурса этого типа: общие плюс свои.
 *
 * @param string $type Слаг типа.
 * @return array<string, array<string, mixed>>
 */
function designstack_core_fields_for_type( string $type ): array {
	return array_filter(
		designstack_core_fields(),
		static fn( $field ) => 'common' === $field['group'] || $field['group'] === $type
	);
}

/**
 * Ресурс без части «Когда не подойдёт» не публикуется (D32).
 *
 * Запись возвращается в «На утверждении», куратор видит сообщение в админке.
 *
 * @param int     $post_id Идентификатор записи.
 * @param WP_Post $post    Запись.
 * @return void
 */
function designstack_core_guard_publish( int $post_id, $post ): void {
	if ( 'publish' !== $post->post_status || wp_is_post_revision( $post_id ) ) {
		return;
	}

	// При импорте запись создаётся раньше своих полей: страж увидел бы пустое
	// «Когда не подойдёт» у каждой записи и отправил весь каталог на утверждение,
	// попутно обнулив слаги. Поля проверяет тот, кто публикует, а не импортёр.
	if ( defined( 'WP_IMPORTING' ) && WP_IMPORTING ) {
		return;
	}

	if ( '' !== (string) designstack_core_get_field( $post_id, 'review_not' ) ) {
		return;
	}

	remove_action( 'save_post_resource', 'designstack_core_guard_publish', 30 );
	// Слаг передаём явно: возврат в «на утверждении» иначе стирает его.
	wp_update_post(
		array(
			'ID'          => $post_id,
			'post_status' => 'pending',
			'post_name'   => $post->post_name,
		)
	);
	add_action( 'save_post_resource', 'designstack_core_guard_publish', 30, 2 );

	set_transient( 'designstack_core_blocked_' . $post_id, 1, MINUTE_IN_SECONDS );
}
add_action( 'save_post_resource', 'designstack_core_guard_publish', 30, 2 );

/**
 * Сообщение куратору, почему запись не опубликовалась.
 *
 * @return void
 */
function designstack_core_blocked_notice(): void {
	$screen = get_current_screen();

	if ( ! $screen || 'resource' !== $screen->post_type || 'post' !== $screen->base ) {
		return;
	}

	$post_id = absint( $_GET['post'] ?? 0 ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended -- только чтение своего же признака.

	if ( ! $post_id || ! get_transient( 'designstack_core_blocked_' . $post_id ) ) {
		return;
	}

	delete_transient( 'designstack_core_blocked_' . $post_id );

	printf(
		'<div class="notice notice-warning"><p>%s</p></div>',
		esc_html__( 'Ресурс вернулся на утверждение: не заполнена часть оценки «Когда не подойдёт». Заполните её и опубликуйте снова.', 'designstack-core' )
	);
}
add_action( 'admin_notices', 'designstack_core_blocked_notice' );

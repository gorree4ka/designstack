<?php
/**
 * Панель «Поля ресурса» в редакторе.
 *
 * Классический метабокс: в блочном редакторе он живёт в ящике «Мета-боксы» внизу,
 * разворот запоминается за куратором (проба `meta-box-block-editor`, D63).
 * Поля не своего типа прячет admin/meta-box.js; без JS видно все.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Регистрирует метабокс полей.
 *
 * @return void
 */
function designstack_core_add_meta_box(): void {
	add_meta_box(
		'designstack_resource_fields',
		__( 'Поля ресурса', 'designstack-core' ),
		'designstack_core_render_meta_box',
		'resource',
		'normal',
		'high'
	);
}
add_action( 'add_meta_boxes_resource', 'designstack_core_add_meta_box' );

/**
 * Рисует панель: общий fieldset и по одному на каждый тип.
 *
 * @param WP_Post $post Запись.
 * @return void
 */
function designstack_core_render_meta_box( $post ): void {
	$post_id = (int) $post->ID;
	$type    = designstack_core_get_type( $post_id );
	$groups  = designstack_core_field_groups();

	wp_nonce_field( 'designstack_core_meta', 'designstack_core_nonce' );

	echo '<div class="ds-core-fields" data-current-type="' . esc_attr( $type ) . '">';
	echo '<p class="description">' . esc_html__( 'Поля показаны по выбранному типу. Тип меняется в панели «Типы» справа.', 'designstack-core' ) . '</p>';

	foreach ( $groups as $group => $title ) {
		$fields = array_filter( designstack_core_fields(), static fn( $field ) => $field['group'] === $group );

		if ( ! $fields ) {
			continue;
		}

		printf(
			'<fieldset class="ds-core-group" data-group="%1$s"><legend>%2$s</legend>',
			esc_attr( $group ),
			esc_html( $title )
		);

		foreach ( $fields as $key => $field ) {
			designstack_core_render_field( $post_id, $key, $field );
		}

		echo '</fieldset>';
	}

	echo '</div>';
}

/**
 * Рисует одно поле по его описанию из реестра.
 *
 * @param int                  $post_id Запись.
 * @param string               $key     Ключ поля.
 * @param array<string, mixed> $field   Описание поля.
 * @return void
 */
function designstack_core_render_field( int $post_id, string $key, array $field ): void {
	$value = designstack_core_get_field( $post_id, $key );
	$id    = 'ds-core-' . $key;
	$name  = 'designstack_core[' . $key . ']';
	$hint  = isset( $field['hint'] ) ? sprintf( '<p class="description" id="%1$s-hint">%2$s</p>', esc_attr( $id ), esc_html( $field['hint'] ) ) : '';
	$aria  = $hint ? ' aria-describedby="' . esc_attr( $id ) . '-hint"' : '';

	echo '<p class="ds-core-field">';

	if ( 'checkbox' !== $field['control'] ) {
		printf( '<label for="%1$s"><strong>%2$s</strong></label><br>', esc_attr( $id ), esc_html( $field['label'] ) );
	}

	switch ( $field['control'] ) {
		case 'url':
		case 'text':
			$printed = is_array( $value ) ? implode( ', ', $value ) : (string) $value;

			printf(
				'<input type="%1$s" id="%2$s" name="%3$s" value="%4$s" class="widefat"%5$s>',
				'url' === $field['control'] ? 'url' : 'text',
				esc_attr( $id ),
				esc_attr( $name ),
				esc_attr( $printed ),
				wp_kses_data( $aria )
			);
			break;

		case 'textarea':
			printf(
				'<textarea id="%1$s" name="%2$s" rows="4" class="widefat"%3$s>%4$s</textarea>',
				esc_attr( $id ),
				esc_attr( $name ),
				wp_kses_data( $aria ),
				esc_textarea( (string) $value )
			);
			break;

		case 'date':
			printf(
				'<input type="date" id="%1$s" name="%2$s" value="%3$s"> <button type="button" class="button ds-core-today" data-target="%1$s">%4$s</button>',
				esc_attr( $id ),
				esc_attr( $name ),
				esc_attr( (string) $value ),
				esc_html__( 'Сегодня', 'designstack-core' )
			);
			break;

		case 'number':
			printf(
				'<input type="number" min="0" step="1" id="%1$s" name="%2$s" value="%3$s">',
				esc_attr( $id ),
				esc_attr( $name ),
				esc_attr( (string) $value )
			);
			break;

		case 'checkbox':
			printf(
				'<label for="%1$s"><input type="checkbox" id="%1$s" name="%2$s" value="1"%3$s> <strong>%4$s</strong></label>',
				esc_attr( $id ),
				esc_attr( $name ),
				checked( (bool) $value, true, false ),
				esc_html( $field['label'] )
			);
			break;

		case 'select':
			$options = designstack_core_enums()[ $field['enum'] ];

			printf( '<select id="%1$s" name="%2$s"%3$s>', esc_attr( $id ), esc_attr( $name ), wp_kses_data( $aria ) );
			printf( '<option value="">%s</option>', esc_html__( '— не заполнено —', 'designstack-core' ) );

			foreach ( $options as $option => $label ) {
				printf(
					'<option value="%1$s"%2$s>%3$s</option>',
					esc_attr( $option ),
					selected( (string) $value, $option, false ),
					esc_html( $label )
				);
			}

			echo '</select>';
			break;

		case 'multiselect':
			$options  = designstack_core_enums()[ $field['enum'] ];
			$selected = (array) $value;

			echo '<span class="ds-core-checks">';

			foreach ( $options as $option => $label ) {
				printf(
					'<label><input type="checkbox" name="%1$s[]" value="%2$s"%3$s> %4$s</label> ',
					esc_attr( $name ),
					esc_attr( $option ),
					checked( in_array( $option, $selected, true ), true, false ),
					esc_html( $label )
				);
			}

			echo '</span>';
			break;

		case 'posts':
			$selected = array_map( 'intval', (array) $value );
			$items    = get_posts(
				array(
					'post_type'   => 'resource',
					'post_status' => 'publish',
					'numberposts' => 200,
					'orderby'     => 'title',
					'order'       => 'ASC',
					'exclude'     => array( $post_id ),
				)
			);

			printf( '<select id="%1$s" name="%2$s[]" multiple size="6" class="widefat"%3$s>', esc_attr( $id ), esc_attr( $name ), wp_kses_data( $aria ) );

			foreach ( $items as $item ) {
				printf(
					'<option value="%1$d"%2$s>%3$s</option>',
					(int) $item->ID,
					selected( in_array( (int) $item->ID, $selected, true ), true, false ),
					esc_html( $item->post_title )
				);
			}

			echo '</select>';
			break;

		case 'terms':
			$selected = array_map( 'intval', (array) $value );
			$terms    = get_terms(
				array(
					'taxonomy'   => $field['taxonomy'],
					'hide_empty' => false,
				)
			);

			printf( '<select id="%1$s" name="%2$s[]" multiple size="4" class="widefat">', esc_attr( $id ), esc_attr( $name ) );

			if ( is_wp_error( $terms ) || ! $terms ) {
				printf( '<option value="" disabled>%s</option>', esc_html__( 'Карта навыков ещё не заведена', 'designstack-core' ) );
			} else {
				foreach ( $terms as $term ) {
					printf(
						'<option value="%1$d"%2$s>%3$s</option>',
						(int) $term->term_id,
						selected( in_array( (int) $term->term_id, $selected, true ), true, false ),
						esc_html( $term->name )
					);
				}
			}

			echo '</select>';
			break;
	}

	echo wp_kses_post( $hint );
	echo '</p>';
}

/**
 * Сохраняет поля панели.
 *
 * @param int $post_id Идентификатор записи.
 * @return void
 */
function designstack_core_save_meta_box( int $post_id ): void {
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}

	$nonce = isset( $_POST['designstack_core_nonce'] )
		? sanitize_text_field( wp_unslash( $_POST['designstack_core_nonce'] ) )
		: '';

	if ( ! $nonce || ! wp_verify_nonce( $nonce, 'designstack_core_meta' ) ) {
		return;
	}

	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	// phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- каждое значение чистит designstack_core_set_field().
	$sent = isset( $_POST['designstack_core'] ) ? wp_unslash( (array) $_POST['designstack_core'] ) : array();

	foreach ( designstack_core_fields() as $key => $field ) {
		if ( 'checkbox' === $field['control'] ) {
			designstack_core_set_field( $post_id, $key, ! empty( $sent[ $key ] ) );

			continue;
		}

		$value = $sent[ $key ] ?? ( empty( $field['multiple'] ) ? '' : array() );

		// Список форматов файла куратор пишет строкой через запятую.
		if ( ! empty( $field['multiple'] ) && is_string( $value ) ) {
			$value = array_filter( array_map( 'trim', explode( ',', $value ) ) );
		}

		designstack_core_set_field( $post_id, $key, $value );
	}
}
add_action( 'save_post_resource', 'designstack_core_save_meta_box', 10 );

/**
 * Подключает скрипт панели только на экране ресурса.
 *
 * @param string $hook Текущий экран.
 * @return void
 */
function designstack_core_meta_box_assets( string $hook ): void {
	if ( ! in_array( $hook, array( 'post.php', 'post-new.php' ), true ) ) {
		return;
	}

	$screen = get_current_screen();

	if ( ! $screen || 'resource' !== $screen->post_type ) {
		return;
	}

	$path = DESIGNSTACK_CORE_DIR . 'admin/meta-box.js';

	wp_enqueue_script(
		'designstack-core-meta-box',
		DESIGNSTACK_CORE_URL . 'admin/meta-box.js',
		array( 'wp-data' ),
		(string) filemtime( $path ),
		true
	);

	// Блочный редактор рисует таксономию своей панелью и метабокс с радиокнопками
	// не показывает, поэтому тип скрипт берёт из хранилища редактора — по номерам термов.
	$types = get_terms(
		array(
			'taxonomy'   => 'resource_type',
			'hide_empty' => false,
		)
	);
	$map   = array();

	if ( ! is_wp_error( $types ) ) {
		foreach ( $types as $term ) {
			$map[ (string) $term->term_id ] = $term->slug;
		}
	}

	wp_localize_script( 'designstack-core-meta-box', 'designstackCoreFields', array( 'types' => $map ) );

	wp_add_inline_style(
		'wp-admin',
		'.ds-core-group{border:1px solid #dcdcde;padding:0 12px 8px;margin:0 0 12px}'
		. '.ds-core-group legend{font-weight:600;padding:0 4px}'
		. '.ds-core-checks label{display:inline-block;margin:0 12px 4px 0}'
		. '.ds-core-field{margin:0 0 18px}'
		. '.ds-core-field .description{margin:4px 0 0}'
	);
}
add_action( 'admin_enqueue_scripts', 'designstack_core_meta_box_assets' );

<?php
/**
 * Применяет демо-контент из scripts/seed_data.json.
 *
 * Запускается только через `python scripts/seed.py` — тот проверяет данные
 * и печатает отчёт. Здесь вся работа идёт функциями плагина designstack-core,
 * поэтому значения проходят ту же санитизацию, что и правки в редакторе.
 *
 * Вызов: tools/wp.cmd --path=wordpress eval-file C:/…/scripts/seed.php <apply|reset>
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

if ( ! function_exists( 'designstack_core_set_field' ) ) {
	echo "ОШИБКА: плагин designstack-core не активен\n";

	return;
}

$ds_mode = $args[0] ?? 'apply';
$ds_file = dirname( __DIR__ ) . '/scripts/seed_data.json';

if ( ! file_exists( $ds_file ) ) {
	$ds_file = 'C:/Projects/DesignSite/scripts/seed_data.json';
}

$ds_data = json_decode( (string) file_get_contents( $ds_file ), true );

if ( ! is_array( $ds_data ) ) {
	echo "ОШИБКА: не читается scripts/seed_data.json\n";

	return;
}

/**
 * Ищет запись по слагу среди любых статусов.
 *
 * @param string $slug Слаг.
 * @param string $type Тип записи.
 * @return int
 */
function designstack_seed_find( string $slug, string $type ): int {
	$found = get_posts(
		array(
			'post_type'      => $type,
			'name'           => $slug,
			'post_status'    => 'any',
			'posts_per_page' => 1,
			'fields'         => 'ids',
		)
	);

	return $found ? (int) $found[0] : 0;
}

// --- Сброс: удаляем только своё.
if ( 'reset' === $ds_mode ) {
	$ds_removed = 0;

	foreach ( array( 'resource', 'post' ) as $ds_type ) {
		$ds_own = get_posts(
			array(
				'post_type'      => $ds_type,
				'post_status'    => 'any',
				'posts_per_page' => -1,
				'fields'         => 'ids',
				'meta_query'     => array(
					array(
						'key'   => '_designstack_seed',
						'value' => '1',
					),
				),
			)
		);

		foreach ( $ds_own as $ds_id ) {
			wp_delete_post( (int) $ds_id, true );
			++$ds_removed;
		}
	}

	echo "created=0 updated=0 removed={$ds_removed}\n";

	return;
}

// --- Наполнение.
$ds_created = 0;
$ds_updated = 0;
$ds_ids     = array();

foreach ( $ds_data['resources'] as $ds_row ) {
	$ds_id = designstack_seed_find( $ds_row['slug'], 'resource' );

	if ( $ds_id ) {
		wp_update_post(
			array(
				'ID'         => $ds_id,
				'post_title' => $ds_row['title'],
			)
		);
		++$ds_updated;
	} else {
		// Создаём черновиком: поля ещё не записаны, а публикация без части
		// «Когда не подойдёт» вернула бы запись на утверждение (D32).
		$ds_id = wp_insert_post(
			array(
				'post_type'   => 'resource',
				'post_status' => 'draft',
				'post_title'  => $ds_row['title'],
				'post_name'   => $ds_row['slug'],
				'post_author' => 1,
			)
		);

		if ( is_wp_error( $ds_id ) || ! $ds_id ) {
			echo "ОШИБКА: не создалась запись {$ds_row['slug']}\n";

			continue;
		}

		++$ds_created;
	}

	$ds_ids[ $ds_row['slug'] ] = (int) $ds_id;

	wp_set_object_terms( $ds_id, $ds_row['type'], 'resource_type', false );
	wp_set_object_terms( $ds_id, $ds_row['topics'], 'topic', false );
	wp_set_object_terms( $ds_id, $ds_row['levels'], 'level', false );

	foreach ( $ds_row['fields'] as $ds_key => $ds_value ) {
		designstack_core_set_field( (int) $ds_id, $ds_key, $ds_value );
	}

	update_post_meta( $ds_id, '_designstack_seed', '1' );

	// Поля на месте — можно публиковать. Слаг передаём явно, иначе WordPress
	// пересоберёт его из русского названия.
	wp_update_post(
		array(
			'ID'          => $ds_id,
			'post_status' => 'publish',
			'post_name'   => $ds_row['slug'],
		)
	);
}

// Аналоги ставим вторым проходом: к этому моменту все записи уже есть.
foreach ( $ds_data['resources'] as $ds_row ) {
	if ( empty( $ds_row['analogs'] ) ) {
		continue;
	}

	$ds_targets = array();

	foreach ( $ds_row['analogs'] as $ds_slug ) {
		if ( isset( $ds_ids[ $ds_slug ] ) ) {
			$ds_targets[] = $ds_ids[ $ds_slug ];
		}
	}

	designstack_core_set_field( $ds_ids[ $ds_row['slug'] ], 'ru_alternative', $ds_targets );
}

// --- Статейные форматы: подборки и дайджест с блоком списка ресурсов.
foreach ( $ds_data['posts'] as $ds_row ) {
	$ds_list = array();

	foreach ( $ds_row['resources'] as $ds_slug ) {
		if ( isset( $ds_ids[ $ds_slug ] ) ) {
			$ds_list[] = $ds_ids[ $ds_slug ];
		}
	}

	$ds_content = '<!-- wp:paragraph -->' . "\n"
		. '<p>' . esc_html( $ds_row['intro'] ) . '</p>' . "\n"
		. '<!-- /wp:paragraph -->' . "\n\n"
		. '<!-- wp:designstack/resource-list ' . wp_json_encode( array( 'ids' => $ds_list, 'layout' => 'grid' ) ) . ' /-->';

	$ds_id = designstack_seed_find( $ds_row['slug'], 'post' );

	$ds_fields = array(
		'post_type'    => 'post',
		'post_status'  => 'publish',
		'post_title'   => $ds_row['title'],
		'post_name'    => $ds_row['slug'],
		'post_excerpt' => $ds_row['excerpt'],
		'post_content' => $ds_content,
		'post_author'  => 1,
	);

	if ( $ds_id ) {
		$ds_fields['ID'] = $ds_id;
		wp_update_post( $ds_fields );
		++$ds_updated;
	} else {
		$ds_id = wp_insert_post( $ds_fields );

		if ( is_wp_error( $ds_id ) || ! $ds_id ) {
			echo "ОШИБКА: не создалась запись {$ds_row['slug']}\n";

			continue;
		}

		++$ds_created;
	}

	wp_set_object_terms( $ds_id, $ds_row['category'], 'category', false );
	update_post_meta( $ds_id, '_designstack_seed', '1' );
}

echo "created={$ds_created} updated={$ds_updated} removed=0\n";

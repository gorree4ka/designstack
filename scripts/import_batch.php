<?php
/**
 * Импорт партии каталога из docs/content/batches/<дата>_<тип>.json.
 *
 * Отличие от scripts/seed.php: записи остаются **черновиками** и не получают метку
 * `_designstack_seed` — это настоящий контент, а не демо, и публикует его куратор
 * после апрува (директива 16, фаза 2). Запись ищется по слагу: повторный запуск
 * обновляет, а не плодит дубли.
 *
 * Вызов: tools/wp.cmd --path=wordpress eval-file C:/…/scripts/import_batch.php <путь к json>
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

if ( ! function_exists( 'designstack_core_set_field' ) ) {
	echo "ОШИБКА: плагин designstack-core не активен\n";

	return;
}

$ds_file = $args[0] ?? '';

if ( ! $ds_file || ! file_exists( $ds_file ) ) {
	echo "ОШИБКА: не найден файл партии: {$ds_file}\n";

	return;
}

$ds_data = json_decode( (string) file_get_contents( $ds_file ), true );

if ( ! is_array( $ds_data ) || empty( $ds_data['resources'] ) ) {
	echo "ОШИБКА: в файле нет раздела resources\n";

	return;
}

$ds_created = 0;
$ds_updated = 0;
$ds_ids     = array();

foreach ( $ds_data['resources'] as $ds_row ) {
	$ds_found = get_posts(
		array(
			'post_type'      => 'resource',
			'name'           => $ds_row['slug'],
			'post_status'    => 'any',
			'posts_per_page' => 1,
			'fields'         => 'ids',
		)
	);

	$ds_id = $ds_found ? (int) $ds_found[0] : 0;

	if ( $ds_id ) {
		wp_update_post(
			array(
				'ID'         => $ds_id,
				'post_title' => $ds_row['title'],
			)
		);
		++$ds_updated;
	} else {
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

	// Слаг задаём явно: из русского названия WordPress соберёт свой.
	wp_update_post(
		array(
			'ID'        => $ds_id,
			'post_name' => $ds_row['slug'],
		)
	);
}

// Аналоги — вторым проходом: к этому моменту записи партии уже существуют.
foreach ( $ds_data['resources'] as $ds_row ) {
	if ( empty( $ds_row['analogs'] ) ) {
		continue;
	}

	$ds_targets = array();

	foreach ( $ds_row['analogs'] as $ds_slug ) {
		if ( isset( $ds_ids[ $ds_slug ] ) ) {
			$ds_targets[] = $ds_ids[ $ds_slug ];

			continue;
		}

		// Аналог может быть уже в каталоге, а не в этой партии.
		$ds_outside = get_posts(
			array(
				'post_type'      => 'resource',
				'name'           => $ds_slug,
				'post_status'    => 'any',
				'posts_per_page' => 1,
				'fields'         => 'ids',
			)
		);

		if ( $ds_outside ) {
			$ds_targets[] = (int) $ds_outside[0];
		} else {
			echo "ВНИМАНИЕ: аналог {$ds_slug} не найден в каталоге\n";
		}
	}

	designstack_core_set_field( $ds_ids[ $ds_row['slug'] ], 'ru_alternative', $ds_targets );
}

echo "создано={$ds_created} обновлено={$ds_updated}\n";

foreach ( $ds_ids as $ds_slug => $ds_post_id ) {
	printf( "  #%d %s (%s)\n", $ds_post_id, $ds_slug, get_post_status( $ds_post_id ) );
}

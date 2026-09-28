<?php
/**
 * Публикует утверждённую партию каталога: дата проверки — день утверждения, статус — «опубликовано».
 *
 * Навык catalog-content, фаза 2: черновик публикуется только после «утвердить» куратора. Партия та же,
 * что заводил `scripts/import_batch.php`, поэтому один и тот же вызов работает локально и на хостинге.
 *
 *   wp eval-file scripts/publish_batch.php <путь к json партии> <ГГГГ-ММ-ДД> [слаг слаг …]
 *
 * Без списка слагов публикуются все записи партии. Запись ищется по слагу среди черновиков и
 * опубликованных: статус `any` в WP-CLI без пользователя черновики не видит (правило в wp-theme.md).
 */

$ds_file  = $args[0] ?? '';
$ds_date  = $args[1] ?? '';
$ds_only  = array_slice( $args, 2 );
$ds_stati = array( 'publish', 'future', 'draft', 'pending', 'private' );

if ( ! $ds_file || ! file_exists( $ds_file ) || ! preg_match( '/^\d{4}-\d{2}-\d{2}$/', $ds_date ) ) {
	echo "нужны путь к партии и дата утверждения ГГГГ-ММ-ДД\n";

	return;
}

$ds_data = json_decode( (string) file_get_contents( $ds_file ), true );

if ( empty( $ds_data['resources'] ) ) {
	echo "в партии нет записей\n";

	return;
}

$ds_done = 0;

foreach ( $ds_data['resources'] as $ds_row ) {
	if ( $ds_only && ! in_array( $ds_row['slug'], $ds_only, true ) ) {
		continue;
	}

	$ds_found = get_posts(
		array(
			'post_type'   => 'resource',
			'name'        => $ds_row['slug'],
			'post_status' => $ds_stati,
			'numberposts' => 1,
		)
	);

	if ( ! $ds_found ) {
		echo "не найдена: {$ds_row['slug']}\n";
		continue;
	}

	$ds_id = (int) $ds_found[0]->ID;

	designstack_core_set_field( $ds_id, 'checked_at', $ds_date );

	// Слаг передаётся явно: смена статуса без него пересобирает post_name (правило в wp-theme.md, §8).
	wp_update_post(
		array(
			'ID'          => $ds_id,
			'post_status' => 'publish',
			'post_name'   => $ds_row['slug'],
		)
	);

	$ds_now = get_post( $ds_id );
	echo "#{$ds_id} {$ds_now->post_name} → {$ds_now->post_status}, проверено {$ds_date}\n";
	++$ds_done;
}

echo "опубликовано: {$ds_done}\n";

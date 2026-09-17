<?php
/**
 * Заводит или обновляет уроки из папки: тело — `<слаг>.body.html`, название и анонс — `<слаг>.body.json`.
 *
 *   wp eval-file scripts/import_lessons.php <папка> [слаг слаг …]
 *
 * Без списка слагов берутся все тела в папке. Навык и ступень читаются из слага:
 * `usability-testing-junior` — навык `usability-testing`, ступень `junior`.
 *
 * Название и анонс идут из файла, а не из аргументов: русская строка с кавычками в аргументе
 * ssh-команды ломается по дороге, а файл доезжает как есть. Поэтому один и тот же скрипт
 * работает и локально, и на хостинге.
 */

$dir   = isset( $args[0] ) ? rtrim( str_replace( '\\', '/', $args[0] ), '/' ) : '';
$slugs = array_slice( $args, 1 );

if ( ! $dir || ! is_dir( $dir ) ) {
	echo "нужна папка с уроками\n";

	return;
}

if ( ! $slugs ) {
	foreach ( glob( $dir . '/*.body.html' ) as $file ) {
		$slugs[] = basename( $file, '.body.html' );
	}
}

foreach ( $slugs as $slug ) {
	if ( ! preg_match( '/^(.+)-(junior|middle|senior)$/', $slug, $parts ) ) {
		echo "слаг без ступени: {$slug}\n";
		continue;
	}

	$body = $dir . '/' . $slug . '.body.html';
	$meta = $dir . '/' . $slug . '.body.json';

	if ( ! file_exists( $body ) || ! file_exists( $meta ) ) {
		echo "нет файлов: {$slug}\n";
		continue;
	}

	$head = json_decode( (string) file_get_contents( $meta ), true );
	$term = get_term_by( 'slug', $parts[1], 'skill' );

	if ( ! $term || ! is_array( $head ) ) {
		echo "нет навыка «{$parts[1]}» или заголовка: {$slug}\n";
		continue;
	}

	$post = get_page_by_path( $slug, OBJECT, 'lesson' );
	$data = array(
		'post_type'    => 'lesson',
		'post_status'  => 'publish',
		'post_name'    => $slug,
		'post_title'   => $head['title'],
		'post_excerpt' => $head['excerpt'],
		'post_content' => (string) file_get_contents( $body ),
	);

	if ( $post ) {
		$data['ID'] = $post->ID;
		$id         = wp_update_post( wp_slash( $data ), true );
	} else {
		$id = wp_insert_post( wp_slash( $data ), true );
	}

	if ( is_wp_error( $id ) ) {
		echo "не вышло: {$slug} — " . $id->get_error_message() . "\n";
		continue;
	}

	update_post_meta( $id, 'lesson_step', $parts[2] );
	wp_set_object_terms( $id, array( (int) $term->term_id ), 'skill' );

	echo ( $post ? 'обновлён' : 'создан' ) . ': ' . $slug . ' → #' . $id . ' · '
		. strlen( get_post_field( 'post_content', $id ) ) . " байт\n";
}

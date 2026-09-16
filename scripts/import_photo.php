<?php
/**
 * Заносит один кадр в медиатеку под его собственным именем и печатает адрес файла.
 *
 * Отличие от `set_banner_photo.php`: тот кладёт снимок в настройку баннера, а этот нужен
 * для фото, которое стоит прямо в тексте страницы. Адрес файла предсказуем (имя не меняется),
 * поэтому одна и та же разметка страницы работает и локально, и на хостинге.
 *
 * Повторный запуск не плодит копий: вложение с тем же именем файла обновляется на месте.
 *
 *   wp eval-file scripts/import_photo.php C:/Projects/DesignSite/docs/content/photos/about-desk.webp "альт" "Заголовок"
 *
 * Требования к кадру — `docs/brand/photo-style.md`.
 */

require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

$file  = isset( $args[0] ) ? $args[0] : '';
$alt   = isset( $args[1] ) ? $args[1] : '';
$title = isset( $args[2] ) ? $args[2] : '';

if ( ! $file || ! file_exists( $file ) ) {
	echo "нужен путь к файлу: {$file}\n";

	return;
}

$size = getimagesize( $file );

if ( ! $size ) {
	echo "это не изображение\n";

	return;
}

if ( ! $alt ) {
	echo "нужен альт: он описывает предмет в кадре, а не настроение\n";

	return;
}

$name = basename( $file );

// Ищем уже загруженный файл с тем же именем: иначе WordPress добавит суффикс,
// адрес поедет, и разметка страницы перестанет совпадать с файлом на хостинге.
$found = get_posts(
	array(
		'post_type'      => 'attachment',
		'post_status'    => 'inherit',
		'posts_per_page' => 1,
		'fields'         => 'ids',
		'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query — разовый импорт, не запрос страницы.
			array(
				'key'     => '_wp_attached_file',
				'value'   => '%/' . $name,
				'compare' => 'LIKE',
			),
		),
	)
);

$old = $found ? (int) $found[0] : 0;

if ( $old ) {
	$path = get_attached_file( $old );

	if ( ! copy( $file, $path ) ) {
		echo "файл не перезаписался: {$path}\n";

		return;
	}

	wp_update_attachment_metadata( $old, wp_generate_attachment_metadata( $old, $path ) );
	update_post_meta( $old, '_wp_attachment_image_alt', $alt );

	if ( $title ) {
		wp_update_post(
			array(
				'ID'         => $old,
				'post_title' => $title,
			)
		);
	}

	echo 'обновлено вложение ' . $old . ', ' . $size[0] . '×' . $size[1] . ', ' . wp_get_attachment_url( $old ) . "\n";
	echo "альт: {$alt}\n";

	return;
}

$upload = wp_upload_bits( $name, null, file_get_contents( $file ) );

if ( ! empty( $upload['error'] ) ) {
	echo 'не сохранилось: ' . $upload['error'] . "\n";

	return;
}

$attachment = wp_insert_attachment(
	array(
		'post_mime_type' => (string) $size['mime'],
		'post_title'     => $title ? $title : $name,
		'post_status'    => 'inherit',
	),
	$upload['file']
);

if ( is_wp_error( $attachment ) || ! $attachment ) {
	echo "вложение не создалось\n";

	return;
}

wp_update_attachment_metadata( $attachment, wp_generate_attachment_metadata( $attachment, $upload['file'] ) );
update_post_meta( $attachment, '_wp_attachment_image_alt', $alt );

echo 'вложение ' . $attachment . ', ' . $size[0] . '×' . $size[1] . ', ' . wp_get_attachment_url( $attachment ) . "\n";
echo "альт: {$alt}\n";

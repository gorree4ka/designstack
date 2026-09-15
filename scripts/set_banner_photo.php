<?php
/**
 * Ставит фото на баннер проверки грейда: кладёт файл в медиатеку и запоминает его в настройке.
 *
 * Требования к кадру — `docs/brand/photo-style.md`. Прежнее фото удаляется, чтобы медиатека
 * не копила сиротливые файлы, как это было с обложками статей.
 *
 *   wp eval-file scripts/set_banner_photo.php C:/Projects/DesignSite/docs/content/photos/banner.jpg
 */

require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

$file = isset( $args[0] ) ? $args[0] : '';
$alt  = isset( $args[1] ) ? $args[1] : 'Распечатки экранов и карточки на рабочем столе';
// Третий аргумент `square` кладёт кадр для узкого экрана: широкий снимок там обрезается до полосы.
$key  = ( isset( $args[2] ) && 'square' === $args[2] ) ? 'designstack_core_banner_photo_square' : 'designstack_core_banner_photo';
$name = ( 'designstack_core_banner_photo_square' === $key ) ? 'grade-banner-square' : 'grade-banner';

if ( ! $file || ! file_exists( $file ) ) {
	echo "нужен путь к файлу: {$file}\n";

	return;
}

$size = getimagesize( $file );

if ( ! $size ) {
	echo "это не изображение\n";

	return;
}

if ( $size[0] < 1200 ) {
	echo "кадр уже 1200 px по ширине: он размылится\n";

	return;
}

$old = (int) get_option( $key, 0 );

$upload = wp_upload_bits( $name . '.' . pathinfo( $file, PATHINFO_EXTENSION ), null, file_get_contents( $file ) );

if ( ! empty( $upload['error'] ) ) {
	echo 'не сохранилось: ' . $upload['error'] . "\n";

	return;
}

$attachment = wp_insert_attachment(
	array(
		'post_mime_type' => (string) $size['mime'],
		'post_title'     => __( 'Баннер проверки грейда', 'designstack-core' ),
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
update_option( $key, $attachment );

if ( $old && $old !== $attachment ) {
	wp_delete_attachment( $old, true );
	echo "прежнее фото удалено\n";
}

echo 'фото баннера: вложение ' . $attachment . ', ' . $size[0] . '×' . $size[1] . ', ' . wp_get_attachment_url( $attachment ) . "\n";
echo "альт: {$alt}\n";

<?php
/**
 * Ставит иконку сайта (фавикон) из PNG: заносит файл в медиатеку и прописывает `site_icon`.
 *
 * WordPress сам нарежет размеры для вкладки, закладок и мобильных экранов, поэтому исходник
 * должен быть не меньше 512×512.
 *
 *   wp eval-file scripts/set_site_icon.php C:/Projects/DesignSite/docs/content/brand/favicon.png
 */

require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

$file = isset( $args[0] ) ? $args[0] : '';

if ( ! $file || ! file_exists( $file ) ) {
	echo "нужен путь к PNG: {$file}\n";

	return;
}

$size = getimagesize( $file );

if ( ! $size || $size[0] < 512 || $size[1] < 512 ) {
	echo "иконка меньше 512×512, WordPress не нарежет размеры\n";

	return;
}

$old = (int) get_option( 'site_icon' );

$upload = wp_upload_bits( 'designstack-mark.png', null, file_get_contents( $file ) );

if ( ! empty( $upload['error'] ) ) {
	echo 'не сохранилось: ' . $upload['error'] . "\n";

	return;
}

$attachment = wp_insert_attachment(
	array(
		'post_mime_type' => 'image/png',
		'post_title'     => __( 'Знак DesignStack', 'designstack-core' ),
		'post_status'    => 'inherit',
	),
	$upload['file']
);

if ( is_wp_error( $attachment ) || ! $attachment ) {
	echo "вложение не создалось\n";

	return;
}

wp_update_attachment_metadata( $attachment, wp_generate_attachment_metadata( $attachment, $upload['file'] ) );
update_option( 'site_icon', $attachment );

if ( $old && $old !== $attachment ) {
	wp_delete_attachment( $old, true );
	echo "прежняя иконка удалена\n";
}

echo 'иконка сайта: вложение ' . $attachment . ', ' . wp_get_attachment_url( $attachment ) . "\n";

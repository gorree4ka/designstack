<?php
/**
 * Заносит картинки из папки в медиатеку и ставит их изображением записи: логотип
 * ресурса или обложку статьи. Имя файла — слаг записи, тип записи вторым аргументом.
 *
 * Логотип хранится штатным «изображением записи»: его видно в админке, можно заменить
 * руками, и рендер карточки сам подставляет картинку вместо буквенной плитки.
 * Иконки собирает `scripts/fetch_logos.py`, имя файла — слаг записи.
 *
 *   wp eval-file scripts/import_logos.php C:/Projects/DesignSite/docs/content/logos
 *   wp eval-file scripts/import_logos.php C:/Projects/DesignSite/docs/content/covers post
 *
 * Без `--force` запись с уже поставленным изображением пропускается.
 */

require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

$dir   = isset( $args[0] ) ? rtrim( $args[0], '/\\' ) : '';
$type  = ( isset( $args[1] ) && ! in_array( $args[1], array( 'force', '--force' ), true ) ) ? $args[1] : 'resource';
$force = in_array( 'force', $args, true ) || in_array( '--force', $args, true );

if ( ! $dir || ! is_dir( $dir ) ) {
	echo "нужна папка с иконками: {$dir}\n";

	return;
}

$files = glob( $dir . '/*.png' );

if ( ! $files ) {
	echo "в папке нет ни одного PNG\n";

	return;
}

$set = 0;
$skipped = 0;
$missing = array();

foreach ( $files as $file ) {
	$slug = basename( $file, '.png' );

	$posts = get_posts( array(
		'name'        => $slug,
		'post_type'   => $type,
		'post_status' => 'any',
		'numberposts' => 1,
	) );

	if ( ! $posts ) {
		$missing[] = $slug;

		continue;
	}

	$post = $posts[0];

	if ( has_post_thumbnail( $post->ID ) && ! $force ) {
		$skipped++;

		continue;
	}

	$suffix = ( 'resource' === $type ) ? '-logo' : '-cover';
	$upload = wp_upload_bits( $slug . $suffix . '.png', null, file_get_contents( $file ) );

	if ( ! empty( $upload['error'] ) ) {
		echo "  {$slug}: не сохранилось — {$upload['error']}\n";

		continue;
	}

	$attachment = wp_insert_attachment(
		array(
			'post_mime_type' => 'image/png',
			/* translators: %s — название записи. */
			'post_title'     => sprintf(
				( 'resource' === $type )
					? __( 'Логотип %s', 'designstack-core' )
					: __( 'Обложка «%s»', 'designstack-core' ),
				$post->post_title
			),
			'post_status'    => 'inherit',
		),
		$upload['file'],
		$post->ID
	);

	if ( is_wp_error( $attachment ) || ! $attachment ) {
		echo "  {$slug}: вложение не создалось\n";

		continue;
	}

	wp_update_attachment_metadata( $attachment, wp_generate_attachment_metadata( $attachment, $upload['file'] ) );
	set_post_thumbnail( $post->ID, $attachment );
	$set++;
}

echo 'поставлено логотипов: ' . $set . ', пропущено (уже есть): ' . $skipped . "\n";

if ( $missing ) {
	echo 'нет записи под файл: ' . implode( ', ', $missing ) . "\n";
}

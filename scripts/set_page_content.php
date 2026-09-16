<?php
/**
 * Записывает содержимое страницы из файла: `docs/content/pages/<slug>.html` → страница `<slug>`.
 *
 * Тексты страниц живут в репозитории, а не только в базе: так правку видно в истории,
 * и одна и та же разметка ложится и локально, и на хостинге.
 *
 *   wp eval-file scripts/set_page_content.php about C:/Projects/DesignSite/docs/content/pages/about.html
 */

$slug = isset( $args[0] ) ? $args[0] : '';
$file = isset( $args[1] ) ? $args[1] : '';

if ( ! $slug || ! $file || ! file_exists( $file ) ) {
	echo "нужен слаг страницы и путь к файлу\n";

	return;
}

$page = get_page_by_path( $slug );

if ( ! $page ) {
	echo "страницы нет: {$slug}\n";

	return;
}

$html = (string) file_get_contents( $file );

if ( '' === trim( $html ) ) {
	echo "файл пуст\n";

	return;
}

$result = wp_update_post(
	array(
		'ID'           => $page->ID,
		'post_content' => $html,
	),
	true
);

if ( is_wp_error( $result ) ) {
	echo 'не записалось: ' . $result->get_error_message() . "\n";

	return;
}

echo 'страница ' . $slug . ' (' . $page->ID . '): ' . strlen( $html ) . " байт\n";

<?php
/**
 * Заводит заголовки для поиска из `docs/content/seo-titles.json` (D198).
 *
 *   wp eval-file scripts/import_seo_titles.php <файл>
 *
 * В файле четыре раздела: `resources` — слаг карточки → заголовок, `terms` — таксономия → слаг → фраза
 * (к фразе раздела и темы сайт сам добавит «: 50 ресурсов»), `pages` и `posts` — слаг страницы или статьи → заголовок.
 * Пишет только поле `seo_title`, запись не пересохраняет: уведомление поиску не уходит само,
 * его отправляет `scripts/indexnow_ping.php` после выката.
 *
 * Строки идут из файла, а не из аргументов: русская строка в аргументе ssh-команды ломается по дороге.
 */

$ds_file = isset( $args[0] ) ? $args[0] : '';

if ( ! $ds_file || ! is_readable( $ds_file ) ) {
	echo "нужен файл с заголовками\n";

	return;
}

$ds_data = json_decode( (string) file_get_contents( $ds_file ), true );

if ( ! is_array( $ds_data ) || empty( $ds_data['resources'] ) ) {
	echo "файл не разобран или пуст\n";

	return;
}

$ds_done    = array( 'карточек' => 0, 'терминов' => 0, 'страниц' => 0, 'статей' => 0 );
$ds_missing = array();
// Список статусов, а не 'any': запрос по слагу без прав читателя молча теряет черновики (правило wp-theme §8).
$ds_status = array( 'publish', 'future', 'draft', 'pending', 'private' );

foreach ( $ds_data['resources'] as $ds_slug => $ds_title ) {
	$ds_ids = get_posts(
		array(
			'post_type'   => 'resource',
			'name'        => $ds_slug,
			'post_status' => $ds_status,
			'fields'      => 'ids',
			'numberposts' => 1,
		)
	);

	if ( ! $ds_ids ) {
		$ds_missing[] = 'resource/' . $ds_slug;
		continue;
	}

	update_post_meta( $ds_ids[0], 'seo_title', $ds_title );
	++$ds_done['карточек'];
}

foreach ( (array) ( $ds_data['terms'] ?? array() ) as $ds_tax => $ds_items ) {
	foreach ( $ds_items as $ds_slug => $ds_phrase ) {
		$ds_term = get_term_by( 'slug', $ds_slug, $ds_tax );

		if ( ! $ds_term ) {
			$ds_missing[] = $ds_tax . '/' . $ds_slug;
			continue;
		}

		update_term_meta( $ds_term->term_id, 'seo_title', $ds_phrase );
		++$ds_done['терминов'];
	}
}

foreach ( (array) ( $ds_data['pages'] ?? array() ) as $ds_slug => $ds_title ) {
	$ds_page = get_page_by_path( $ds_slug );

	if ( ! $ds_page ) {
		$ds_missing[] = 'page/' . $ds_slug;
		continue;
	}

	update_post_meta( $ds_page->ID, 'seo_title', $ds_title );
	++$ds_done['страниц'];
}

foreach ( (array) ( $ds_data['posts'] ?? array() ) as $ds_slug => $ds_title ) {
	$ds_ids = get_posts(
		array(
			'post_type'   => 'post',
			'name'        => $ds_slug,
			'post_status' => $ds_status,
			'fields'      => 'ids',
			'numberposts' => 1,
		)
	);

	if ( ! $ds_ids ) {
		$ds_missing[] = 'post/' . $ds_slug;
		continue;
	}

	update_post_meta( $ds_ids[0], 'seo_title', $ds_title );
	++$ds_done['статей'];
}

foreach ( $ds_done as $ds_what => $ds_n ) {
	echo "{$ds_what}: {$ds_n}\n";
}

echo 'не найдено: ' . count( $ds_missing ) . ( $ds_missing ? ' — ' . implode( ', ', $ds_missing ) : '' ) . "\n";

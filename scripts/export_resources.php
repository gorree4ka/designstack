<?php
/**
 * Выгружает каталог в JSON для разметки навыками карты компетенций.
 *
 * Поля — те, по которым решается, какой навык поднимает ресурс: имя, тип, темы, грейд
 * и начало вердикта. Полные тексты не нужны и только раздувают файл.
 *
 *   wp eval-file scripts/export_resources.php C:/Projects/DesignSite/.tmp/resources.json
 */

$out = isset( $args[0] ) ? $args[0] : '';

if ( ! $out ) {
	echo "нужен путь, куда писать JSON\n";

	return;
}

$posts = get_posts(
	array(
		'post_type'      => 'resource',
		'post_status'    => 'publish',
		'numberposts'    => -1,
		'orderby'        => 'title',
		'order'          => 'ASC',
	)
);

$rows = array();

foreach ( $posts as $post ) {
	$verdict = (string) get_post_meta( $post->ID, 'verdict', true );

	$rows[] = array(
		'slug'    => $post->post_name,
		'title'   => $post->post_title,
		'type'    => implode( ',', wp_get_post_terms( $post->ID, 'resource_type', array( 'fields' => 'slugs' ) ) ),
		'topics'  => implode( ',', wp_get_post_terms( $post->ID, 'topic', array( 'fields' => 'slugs' ) ) ),
		'level'   => implode( ',', wp_get_post_terms( $post->ID, 'level', array( 'fields' => 'slugs' ) ) ),
		'verdict' => mb_substr( wp_strip_all_tags( $verdict ), 0, 110 ),
		'skills'  => wp_get_post_terms( $post->ID, 'skill', array( 'fields' => 'slugs' ) ),
	);
}

file_put_contents( $out, wp_json_encode( $rows, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE ) );

echo 'выгружено записей: ' . count( $rows ) . " → {$out}\n";

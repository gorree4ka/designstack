<?php
// Меню блочной темы — запись wp_navigation с блоками ссылок; классическое меню core/navigation не читает.
$items = array(
	array( 'Инструменты', '/tools/' ),
	array( 'Учёба', '/learn/' ),
	array( 'Ассеты', '/assets/' ),
	array( 'Сообщества', '/community/' ),
	array( 'Подборки', '/collections/' ),
	array( 'Дайджест', '/digest/' ),
	array( 'О проекте', '/about/' ),
);

$blocks = '';
foreach ( $items as $item ) {
	$blocks .= sprintf(
		'<!-- wp:navigation-link {"label":"%1$s","url":"%2$s","kind":"custom","isTopLevelLink":true} /-->' . "\n",
		esc_attr( $item[0] ),
		esc_url_raw( home_url( $item[1] ) )
	);
}

$existing = get_posts(
	array(
		'post_type'      => 'wp_navigation',
		'name'           => 'razdely-kataloga',
		'post_status'    => 'any',
		'posts_per_page' => 1,
	)
);

$data = array(
	'post_type'    => 'wp_navigation',
	'post_title'   => 'Разделы каталога',
	'post_name'    => 'razdely-kataloga',
	'post_status'  => 'publish',
	'post_content' => trim( $blocks ),
);

if ( $existing ) {
	$data['ID'] = $existing[0]->ID;
	$id         = wp_update_post( $data, true );
} else {
	$id = wp_insert_post( $data, true );
}

if ( is_wp_error( $id ) ) {
	echo 'ошибка: ' . $id->get_error_message() . PHP_EOL;
	return;
}

echo 'wp_navigation id ' . $id . ', ссылок ' . substr_count( get_post( $id )->post_content, 'wp:navigation-link' ) . PHP_EOL;

// Классическое меню этапа 11 больше не нужно: core/navigation его не читает.
$legacy = wp_get_nav_menu_object( 'Разделы каталога' );
if ( $legacy ) {
	wp_delete_nav_menu( $legacy->term_id );
	echo 'классическое меню удалено' . PHP_EOL;
}

echo 'рендер: ' . substr( preg_replace( '/\s+/', ' ', trim( do_blocks( '<!-- wp:navigation {"ref":' . $id . ',"overlayMenu":"never"} /-->' ) ) ), 0, 300 ) . PHP_EOL;

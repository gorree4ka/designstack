<?php
/**
 * Сообщает Яндексу (IndexNow) об адресах, у которых поменялся заголовок для поиска (D198).
 *
 *   wp eval-file scripts/indexnow_ping.php            # все адреса с полем seo_title
 *   wp eval-file scripts/indexnow_ping.php <адрес> …  # только перечисленные
 *
 * Правка поля не пересохраняет запись, поэтому уведомление при публикации (`includes/indexnow.php`)
 * не срабатывает — после выката его отправляют этим скриптом. Работает только на продакшене:
 * с локального сайта `designstack_core_indexnow_submit()` запрос не отправит и скажет об этом.
 */

$ds_urls = array_values( array_filter( $args, static fn( $a ) => 0 === strpos( $a, 'http' ) ) );

if ( ! $ds_urls ) {
	$ds_ids = get_posts(
		array(
			'post_type'   => array( 'resource', 'page', 'post' ),
			'post_status' => 'publish',
			'numberposts' => -1,
			'fields'      => 'ids',
			'meta_key'    => 'seo_title', // phpcs:ignore WordPress.DB.SlowDBQuery
		)
	);

	foreach ( $ds_ids as $ds_id ) {
		$ds_urls[] = (string) get_permalink( $ds_id );
	}

	foreach ( array( 'resource_type', 'topic', 'category' ) as $ds_tax ) {
		foreach ( get_terms( array( 'taxonomy' => $ds_tax, 'meta_key' => 'seo_title', 'hide_empty' => false ) ) as $ds_term ) { // phpcs:ignore WordPress.DB.SlowDBQuery
			$ds_urls[] = (string) get_term_link( $ds_term );
		}
	}
}

$ds_codes = array();

foreach ( designstack_core_indexnow_submit( $ds_urls ) as $ds_row ) {
	$ds_code              = (string) $ds_row['code'];
	$ds_codes[ $ds_code ] = ( $ds_codes[ $ds_code ] ?? 0 ) + 1;

	if ( ! in_array( $ds_code, array( '200', '202' ), true ) ) {
		echo '  ' . $ds_row['url'] . ' — ' . $ds_code . "\n";
	}
}

echo 'адресов: ' . count( array_unique( $ds_urls ) ) . '; ответы: ';
foreach ( $ds_codes as $ds_code => $ds_n ) {
	echo $ds_code . ' × ' . $ds_n . '  ';
}
echo "\n";

<?php
/**
 * Разметка schema.org: один блок JSON-LD на страницу.
 *
 * Плагин-помощник о наших типах записей ничего не знает, поэтому разметку пишем
 * сами (D119). Правило одно: описываем то, что есть в карточке, а не то, что
 * хочется поисковику. Выдуманный рейтинг или цена, которой нет на странице, —
 * повод для санкций, а не для сниппета.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Печатает граф разметки.
 *
 * @return void
 */
function designstack_core_schema(): void {
	if ( is_404() || is_search() || is_page( array( 'styleguide', 'thanks' ) ) ) {
		return;
	}

	$graph = array_values( array_filter( array_merge(
		designstack_core_schema_site(),
		designstack_core_schema_entity(),
		designstack_core_schema_breadcrumbs()
	) ) );

	if ( ! $graph ) {
		return;
	}

	printf(
		'<script type="application/ld+json">%s</script>' . "\n",
		wp_json_encode(
			array(
				'@context' => 'https://schema.org',
				'@graph'   => $graph,
			),
			JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
		)
	);
}
add_action( 'wp_head', 'designstack_core_schema', 5 );

/**
 * Сайт и издатель — на всех страницах: по ним поисковик связывает страницы в один ресурс.
 *
 * @return array<int, array<string, mixed>>
 */
function designstack_core_schema_site(): array {
	$home = home_url( '/' );

	$site = array(
		'@type'       => 'WebSite',
		'@id'         => $home . '#website',
		'url'         => $home,
		'name'        => get_bloginfo( 'name' ),
		'description' => get_bloginfo( 'description' ),
		'inLanguage'  => 'ru-RU',
		'publisher'   => array( '@id' => $home . '#org' ),
	);

	// Поле поиска в сниппете показывают только тем сайтам, у которых поиск работает
	// по адресу, — наш работает, поэтому заявляем честно.
	$site['potentialAction'] = array(
		'@type'       => 'SearchAction',
		'target'      => array(
			'@type'       => 'EntryPoint',
			'urlTemplate' => home_url( '/search/?s={search_term_string}' ),
		),
		'query-input' => 'required name=search_term_string',
	);

	$org = array(
		'@type' => 'Organization',
		'@id'   => $home . '#org',
		'name'  => get_bloginfo( 'name' ),
		'url'   => $home,
	);

	return array( $site, $org );
}

/**
 * Сущность страницы: ресурс, статья, раздел.
 *
 * @return array<int, array<string, mixed>>
 */
function designstack_core_schema_entity(): array {
	if ( is_singular( 'resource' ) ) {
		return array( designstack_core_schema_resource( get_queried_object_id() ) );
	}

	if ( is_singular( 'post' ) ) {
		return designstack_core_schema_article( get_queried_object_id() );
	}

	if ( is_front_page() || designstack_core_archive_term() ) {
		return designstack_core_schema_listing();
	}

	return array();
}

/**
 * Запись каталога. Тип schema.org зависит от типа ресурса.
 *
 * @param int $id Идентификатор записи.
 * @return array<string, mixed>
 */
function designstack_core_schema_resource( int $id ): array {
	$type     = designstack_core_get_type( $id );
	$url      = (string) get_permalink( $id );
	$site     = (string) designstack_core_get_field( $id, 'url' );
	$verdict  = (string) designstack_core_get_field( $id, 'verdict' );
	$language = (string) designstack_core_get_field( $id, 'language' );

    $map = array(
		'tool'      => 'SoftwareApplication',
		'learning'  => 'CreativeWork',
		'asset'     => 'CreativeWork',
		'community' => 'Organization',
	);

	$node = array(
		'@type'       => $map[ $type ] ?? 'CreativeWork',
		'@id'         => $url . '#item',
		'name'        => get_the_title( $id ),
		'description' => $verdict,
		'url'         => $site ? $site : $url,
		'mainEntityOfPage' => $url,
	);

	if ( 'multi' !== $language && '' !== $language ) {
		$node['inLanguage'] = 'ru' === $language ? 'ru-RU' : 'en';
	}

	if ( 'tool' === $type ) {
		$node['applicationCategory'] = 'DesignApplication';
		$platforms                   = (array) designstack_core_get_field( $id, 'platforms' );

		if ( $platforms ) {
			$node['operatingSystem'] = implode( ', ', $platforms );
		}
	}

	if ( 'learning' === $type ) {
		$format = (string) designstack_core_get_field( $id, 'format' );

		if ( 'course' === $format ) {
			$node['@type'] = 'Course';
			// Курс без сведений о форме обучения Google считает неполным.
			$node['hasCourseInstance'] = array(
				'@type'              => 'CourseInstance',
				'courseMode'         => 'online',
				'courseWorkload'     => (string) designstack_core_get_field( $id, 'duration' ),
			);
			$node['provider'] = array( '@type' => 'Organization', 'name' => get_the_title( $id ) );
		} elseif ( 'book' === $format ) {
			$node['@type'] = 'Book';
		}
	}

	if ( 'asset' === $type ) {
		$license = (string) designstack_core_get_field( $id, 'license' );

		if ( $license ) {
			$node['license'] = designstack_core_enum_label( 'license', $license );
		}
	}

	$offer = designstack_core_schema_offer( $id );

	if ( $offer ) {
		$node['offers'] = $offer;
	}

	return $node;
}

/**
 * Цена: только то, что человек видит в карточке.
 *
 * Точную сумму не заявляем — в `price_note` она словами и с оговорками
 * («при оплате за год», «за редактора»), а числом в разметке это стало бы
 * обещанием, которого сайт не даёт.
 *
 * @param int $id Идентификатор записи.
 * @return array<string, mixed>
 */
function designstack_core_schema_offer( int $id ): array {
	$pricing = (string) designstack_core_get_field( $id, 'pricing' );

	if ( '' === $pricing ) {
		return array();
	}

	$offer = array(
		'@type'         => 'Offer',
		'availability'  => 'https://schema.org/InStock',
		'category'      => designstack_core_enum_label( 'pricing', $pricing ),
	);

	if ( 'free' === $pricing ) {
		$offer['price']         = '0';
		$offer['priceCurrency'] = 'RUB';
	}

	$note = (string) designstack_core_get_field( $id, 'price_note' );

	if ( '' !== $note ) {
		$offer['description'] = $note;
	}

	return $offer;
}

/**
 * Статья редакции: подборка, выпуск дайджеста, обзор.
 *
 * @param int $id Идентификатор записи.
 * @return array<int, array<string, mixed>>
 */
function designstack_core_schema_article( int $id ): array {
	$url  = (string) get_permalink( $id );
	$home = home_url( '/' );

	$article = array(
		'@type'            => 'Article',
		'@id'              => $url . '#article',
		'headline'         => get_the_title( $id ),
		'description'      => get_the_excerpt( $id ),
		'datePublished'    => get_the_date( 'c', $id ),
		'dateModified'     => get_the_modified_date( 'c', $id ),
		'inLanguage'       => 'ru-RU',
		'mainEntityOfPage' => $url,
		'publisher'        => array( '@id' => $home . '#org' ),
		'author'           => array( '@id' => $home . '#org' ),
	);

	$out  = array( $article );
	$list = designstack_core_schema_item_list( designstack_core_post_resource_ids( $id ), $url );

	if ( $list ) {
		$out[] = $list;
	}

	return $out;
}

/**
 * Идентификаторы ресурсов, которые запись показывает блоками «список ресурсов».
 *
 * @param int $id Идентификатор записи.
 * @return array<int, int>
 */
function designstack_core_post_resource_ids( int $id ): array {
	$post = get_post( $id );

	if ( ! $post ) {
		return array();
	}

	$ids = array();

	foreach ( parse_blocks( $post->post_content ) as $block ) {
		if ( 'designstack/resource-list' !== ( $block['blockName'] ?? '' ) ) {
			continue;
		}

		foreach ( (array) ( $block['attrs']['ids'] ?? array() ) as $value ) {
			$ids[] = (int) $value;
		}
	}

	return array_values( array_unique( array_filter( $ids ) ) );
}

/**
 * Раздел каталога или главная: список того, что на странице.
 *
 * @return array<int, array<string, mixed>>
 */
function designstack_core_schema_listing(): array {
	global $wp_query;

	$url  = designstack_core_current_url();
	$term = designstack_core_archive_term();

	$page = array(
		'@type'      => 'CollectionPage',
		'@id'        => $url . '#page',
		'url'        => $url,
		'name'       => $term ? designstack_core_archive_title() : get_bloginfo( 'name' ),
		'inLanguage' => 'ru-RU',
		'isPartOf'   => array( '@id' => home_url( '/' ) . '#website' ),
	);

	$ids = array();

	foreach ( (array) $wp_query->posts as $item ) {
		if ( $item instanceof WP_Post && 'resource' === $item->post_type ) {
			$ids[] = (int) $item->ID;
		}
	}

	$out  = array( $page );
	$list = designstack_core_schema_item_list( $ids, $url );

	if ( $list ) {
		$out[] = $list;
	}

	return $out;
}

/**
 * Список записей: только то, что реально показано на этой странице.
 *
 * @param array<int, int> $ids Идентификаторы.
 * @param string          $url Адрес страницы.
 * @return array<string, mixed>
 */
function designstack_core_schema_item_list( array $ids, string $url ): array {
	if ( ! $ids ) {
		return array();
	}

	$items = array();
	$n     = 0;

	foreach ( $ids as $id ) {
		if ( 'publish' !== get_post_status( $id ) ) {
			continue;
		}

		++$n;
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => $n,
			'url'      => (string) get_permalink( $id ),
			'name'     => get_the_title( $id ),
		);
	}

	if ( ! $items ) {
		return array();
	}

	return array(
		'@type'           => 'ItemList',
		'@id'             => $url . '#list',
		'numberOfItems'   => count( $items ),
		'itemListElement' => $items,
	);
}

/**
 * Хлебные крошки: та же цепочка, что рисует страница.
 *
 * Собираем здесь своими руками: `designstack_core_breadcrumb_items()` — это фильтр
 * над готовым списком блока, вызвать его без списка нельзя.
 *
 * @return array<int, array<string, mixed>>
 */
function designstack_core_schema_breadcrumbs(): array {
	if ( is_front_page() ) {
		return array();
	}

	$home  = home_url( '/' );
	$chain = array( array( 'name' => __( 'Главная', 'designstack-core' ), 'item' => $home ) );

	if ( is_singular( 'resource' ) ) {
		$id   = get_queried_object_id();
		$type = designstack_core_get_type( $id );
		$term = $type ? get_term_by( 'slug', $type, 'resource_type' ) : null;

		if ( $term instanceof WP_Term ) {
			$chain[] = array(
				'name' => designstack_core_section_name( $term->slug ),
				'item' => (string) get_term_link( $term ),
			);
		}

		$chain[] = array( 'name' => get_the_title( $id ) );
	} elseif ( is_singular( 'post' ) ) {
		$cats = get_the_category( get_queried_object_id() );

		if ( $cats ) {
			$chain[] = array( 'name' => $cats[0]->name, 'item' => (string) get_category_link( $cats[0] ) );
		}

		$chain[] = array( 'name' => get_the_title() );
	} elseif ( is_page() ) {
		$chain[] = array( 'name' => get_the_title() );
	} else {
		$term = designstack_core_archive_term();

		if ( ! $term ) {
			return array();
		}

		$chain[] = array( 'name' => designstack_core_archive_title() );
	}

	$list = array();
	$n    = 0;

	foreach ( $chain as $item ) {
		++$n;
		$node = array(
			'@type'    => 'ListItem',
			'position' => $n,
			'name'     => (string) $item['name'],
		);

		if ( ! empty( $item['item'] ) ) {
			$node['item'] = (string) $item['item'];
		}

		$list[] = $node;
	}

	return array(
		array(
			'@type'           => 'BreadcrumbList',
			'@id'             => designstack_core_current_url() . '#crumbs',
			'itemListElement' => $list,
		),
	);
}

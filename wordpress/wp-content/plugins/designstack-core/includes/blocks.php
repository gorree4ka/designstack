<?php
/**
 * Блоки каталога: регистрация из папок с block.json.
 *
 * Сборки нет: editor.js пишется обычным JS, зависимости перечислены рядом
 * в editor.asset.php — без этого файла блок не попадает в реестр редактора
 * и ошибки в консоли при этом не видно (проба `dynamic-block-no-build`, D63).
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Имена блоков плагина.
 *
 * @return array<int, string>
 */
function designstack_core_block_names(): array {
	return array(
		'resource-list',
		'resource-meta',
		'ru-status',
		'suggest-form',
		'archive-header',
		'filter-panel',
		'filter-chips',
		'pagination',
		'resource-hero',
		'curator-review',
		'resource-analogs',
		'search-form',
		'starter-set',
		'checked-week',
		'post-list',
		'subscribe',
		'entry-header',
		'lesson-header',
		'lesson-nav',
		'skills-map',
		'issue-nav',
		'post-archive',
		'search-results',
		'not-found',
		'sort',
		'grade-check',
		'grade-banner',
	);
}

/**
 * Регистрирует блоки и их категорию.
 *
 * @return void
 */
function designstack_core_register_blocks(): void {
	foreach ( designstack_core_block_names() as $name ) {
		$path = DESIGNSTACK_CORE_DIR . 'blocks/' . $name;

		if ( is_dir( $path ) ) {
			register_block_type( $path );
		}
	}
}
add_action( 'init', 'designstack_core_register_blocks', 20 );

/**
 * Своя категория блоков в инсертере.
 *
 * @param array<int, array<string, mixed>> $categories Категории.
 * @return array<int, array<string, mixed>>
 */
function designstack_core_block_category( array $categories ): array {
	array_unshift(
		$categories,
		array(
			'slug'  => 'designstack',
			'title' => __( 'DesignStack', 'designstack-core' ),
			'icon'  => null,
		)
	);

	return $categories;
}
add_filter( 'block_categories_all', 'designstack_core_block_category' );

/**
 * Справочники для панелей блоков в редакторе.
 *
 * Списки собираются на сервере: редактор не должен знать, где лежат слаги.
 *
 * @return void
 */
function designstack_core_block_editor_data(): void {
	$terms = static function ( string $taxonomy ): array {
		$found = get_terms(
			array(
				'taxonomy'   => $taxonomy,
				'hide_empty' => false,
			)
		);

		if ( is_wp_error( $found ) ) {
			return array();
		}

		$map = array();

		foreach ( $found as $term ) {
			$map[ $term->slug ] = $term->name;
		}

		return $map;
	};

	$enums = designstack_core_enums();

	$data = array(
		'types'      => $terms( 'resource_type' ),
		'topics'     => $terms( 'topic' ),
		'levels'     => $terms( 'level' ),
		'pricing'    => $enums['pricing'],
		'ru_open'    => $enums['ru_open'],
		'ru_payment' => $enums['ru_payment'],
	);

	wp_add_inline_script(
		'wp-blocks',
		'window.designstackCoreBlocks = ' . wp_json_encode( $data ) . ';',
		'before'
	);
}
add_action( 'enqueue_block_editor_assets', 'designstack_core_block_editor_data' );

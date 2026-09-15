<?php
/**
 * Проверка грейда: данные карты компетенций и подбор материалов к навыку.
 *
 * Вопросы и варианты ответа собираются скриптом `scripts/render_skills_map.py` из
 * `docs/skills-map/map.md` в `data/skills-map.php` — один источник и для документа, и для сайта.
 * Грейд варианта в разметку страницы не попадает: подсказка рядом с ответом ломает измерение (D142).
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Карта компетенций: области, навыки, варианты ответа.
 *
 * @return array<int, array<string, mixed>>
 */
function designstack_core_skills_map(): array {
	static $map = null;

	if ( null !== $map ) {
		return $map;
	}

	$file = DESIGNSTACK_CORE_DIR . 'data/skills-map.php';
	$map  = file_exists( $file ) ? (array) require $file : array();

	return $map;
}

/**
 * Материалы каталога по навыкам: слаг навыка → записи, которые его поднимают.
 *
 * Один запрос на весь каталог вместо запроса на каждый из 37 навыков. Учебные материалы идут
 * первыми: в плане развития читать полезнее, чем ставить инструмент.
 *
 * @param int $limit Сколько записей оставить на навык.
 * @return array<string, array<int, array<string, string>>>
 */
function designstack_core_skill_resources( int $limit = 3 ): array {
	$posts = get_posts(
		array(
			'post_type'      => 'resource',
			'post_status'    => 'publish',
			'numberposts'    => -1,
			'orderby'        => 'title',
			'order'          => 'ASC',
			'tax_query'      => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_tax_query
				array(
					'taxonomy' => 'skill',
					'operator' => 'EXISTS',
				),
			),
		)
	);

	$weight = array(
		'learning'  => 0,
		'tool'      => 1,
		'asset'     => 2,
		'community' => 3,
	);

	$rows = array();

	foreach ( $posts as $post ) {
		$types = wp_get_post_terms( $post->ID, 'resource_type', array( 'fields' => 'slugs' ) );
		$type  = $types ? (string) $types[0] : '';

		foreach ( wp_get_post_terms( $post->ID, 'skill', array( 'fields' => 'slugs' ) ) as $slug ) {
			$rows[ $slug ][] = array(
				'title'  => get_the_title( $post ),
				'url'    => (string) get_permalink( $post ),
				'type'   => $type,
				'weight' => isset( $weight[ $type ] ) ? $weight[ $type ] : 9,
			);
		}
	}

	foreach ( $rows as $slug => $list ) {
		usort(
			$list,
			static function ( array $a, array $b ): int {
				return $a['weight'] <=> $b['weight'];
			}
		);

		$rows[ $slug ] = array_slice( $list, 0, $limit );
	}

	return $rows;
}

/**
 * Подпись типа записи для списка материалов.
 *
 * @param string $type Слаг типа.
 * @return string
 */
function designstack_core_skill_type_label( string $type ): string {
	$labels = array(
		'learning'  => __( 'учёба', 'designstack-core' ),
		'tool'      => __( 'инструмент', 'designstack-core' ),
		'asset'     => __( 'ассет', 'designstack-core' ),
		'community' => __( 'сообщество', 'designstack-core' ),
	);

	return isset( $labels[ $type ] ) ? $labels[ $type ] : '';
}

/**
 * Сколько в карте навыков.
 *
 * @return int
 */
function designstack_core_skills_count(): int {
	$n = 0;

	foreach ( designstack_core_skills_map() as $area ) {
		$n += count( $area['skills'] );
	}

	return $n;
}

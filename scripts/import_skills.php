<?php
/**
 * Заводит термы таксономии `skill` из выгрузки карты компетенций.
 *
 * Источник — `docs/skills-map/map.md`, выгрузку делает `scripts/render_skills_map.py --terms`.
 * Сначала создаются области, потом навыки: у навыка область указана родителем (D62).
 * Повторный запуск не плодит дубли — терм ищется по слагу и обновляется.
 *
 *   wp eval-file scripts/import_skills.php C:/Projects/DesignSite/.tmp/skills-terms.json
 */

$file = isset( $args[0] ) ? $args[0] : '';

if ( ! $file || ! file_exists( $file ) ) {
	echo "нужен путь к JSON с термами: {$file}\n";

	return;
}

$terms = json_decode( (string) file_get_contents( $file ), true );

if ( ! is_array( $terms ) || ! $terms ) {
	echo "выгрузка пустая или не разбирается\n";

	return;
}

if ( ! taxonomy_exists( 'skill' ) ) {
	echo "таксономия skill не зарегистрирована: плагин designstack-core выключен?\n";

	return;
}

$made    = 0;
$updated = 0;
$failed  = 0;
$ids     = array();

// Два прохода: сначала области, потом навыки — иначе родителя ещё нет.
foreach ( array( '', 'child' ) as $pass ) {
	foreach ( $terms as $term ) {
		$is_child = '' !== $term['parent'];

		if ( ( 'child' === $pass ) !== $is_child ) {
			continue;
		}

		$parent = 0;

		if ( $is_child ) {
			if ( ! isset( $ids[ $term['parent'] ] ) ) {
				echo "  нет области {$term['parent']} для навыка {$term['slug']}\n";
				$failed++;

				continue;
			}

			$parent = $ids[ $term['parent'] ];
		}

		$existing = get_term_by( 'slug', $term['slug'], 'skill' );

		$fields = array(
			'name'        => $term['name'],
			'slug'        => $term['slug'],
			'description' => $term['description'],
			'parent'      => $parent,
		);

		if ( $existing ) {
			$result = wp_update_term( $existing->term_id, 'skill', $fields );
			$updated++;
		} else {
			$result = wp_insert_term( $term['name'], 'skill', $fields );
			$made++;
		}

		if ( is_wp_error( $result ) ) {
			echo "  {$term['slug']}: " . $result->get_error_message() . "\n";
			$failed++;

			continue;
		}

		$ids[ $term['slug'] ] = (int) $result['term_id'];
	}
}

echo "создано: {$made}, обновлено: {$updated}, не вышло: {$failed}\n";
echo 'термов в таксономии: ' . wp_count_terms( array( 'taxonomy' => 'skill', 'hide_empty' => false ) ) . "\n";

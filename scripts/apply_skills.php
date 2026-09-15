<?php
/**
 * Проставляет записям каталога навыки карты компетенций.
 *
 * Вход — файл `.tmp/skills-assign.json`: предложение `scripts/suggest_skills.py` после вычитки.
 * Навык ставится записям всех типов, ступень — только учебным материалам (D26): навыки материала
 * попадают в поле того грейда, на который материал рассчитан по таксономии `level`.
 *
 *   wp eval-file scripts/apply_skills.php C:/Projects/DesignSite/.tmp/skills-assign.json
 */

$file = isset( $args[0] ) ? $args[0] : '';

if ( ! $file || ! file_exists( $file ) ) {
	echo "нужен путь к JSON с разметкой: {$file}\n";

	return;
}

$rows = json_decode( (string) file_get_contents( $file ), true );

if ( ! is_array( $rows ) || ! $rows ) {
	echo "разметка пустая или не разбирается\n";

	return;
}

$steps   = array( 'junior', 'middle', 'senior' );
$marked  = 0;
$stepped = 0;
$missing = 0;
$skipped = array();

foreach ( $rows as $row ) {
	$posts = get_posts(
		array(
			'name'        => $row['slug'],
			'post_type'   => 'resource',
			'post_status' => 'any',
			'numberposts' => 1,
		)
	);

	if ( ! $posts ) {
		$skipped[] = $row['slug'];
		$missing++;

		continue;
	}

	$id = (int) $posts[0]->ID;

	wp_set_object_terms( $id, $row['skills'], 'skill', false );
	$marked++;

	if ( false === strpos( (string) $row['type'], 'learning' ) ) {
		continue;
	}

	$ids = array();

	foreach ( $row['skills'] as $slug ) {
		$term = get_term_by( 'slug', $slug, 'skill' );

		if ( $term ) {
			$ids[] = (int) $term->term_id;
		}
	}

	$levels = array_filter( explode( ',', (string) $row['level'] ) );
	$touched = false;

	foreach ( $steps as $step ) {
		$value = in_array( $step, $levels, true ) ? $ids : array();

		designstack_core_set_field( $id, 'skill_' . $step, $value );

		if ( $value ) {
			$touched = true;
		}
	}

	if ( $touched ) {
		$stepped++;
	}
}

echo "размечено записей: {$marked}, из них учебных со ступенью: {$stepped}\n";

if ( $missing ) {
	echo "не найдено в каталоге: {$missing} — " . implode( ', ', $skipped ) . "\n";
}

$empty = 0;

foreach ( get_posts( array( 'post_type' => 'resource', 'post_status' => 'publish', 'numberposts' => -1, 'fields' => 'ids' ) ) as $id ) {
	if ( ! wp_get_post_terms( $id, 'skill', array( 'fields' => 'ids' ) ) ) {
		$empty++;
	}
}

echo "записей без навыка осталось: {$empty}\n";

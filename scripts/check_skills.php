<?php
/**
 * Проверяет разметку каталога навыками карты компетенций.
 *
 * Правило: у записи любого типа стоит навык, у учебного материала — ещё и ступень (D26).
 * Без этой проверки правило остаётся пожеланием: новая запись молча выпадет из программы развития.
 *
 *   wp eval-file scripts/check_skills.php
 */

$ids = get_posts(
	array(
		'post_type'   => 'resource',
		'post_status' => 'publish',
		'numberposts' => -1,
		'fields'      => 'ids',
	)
);

$no_skill = array();
$no_step  = array();

foreach ( $ids as $id ) {
	if ( ! wp_get_post_terms( $id, 'skill', array( 'fields' => 'ids' ) ) ) {
		$no_skill[] = get_the_title( $id );

		continue;
	}

	if ( ! has_term( 'learning', 'resource_type', $id ) ) {
		continue;
	}

	$has_step = false;

	foreach ( array( 'junior', 'middle', 'senior' ) as $step ) {
		if ( get_post_meta( $id, 'skill_' . $step ) ) {
			$has_step = true;

			break;
		}
	}

	if ( ! $has_step ) {
		$no_step[] = get_the_title( $id );
	}
}

printf( "записей проверено: %d\n", count( $ids ) );
printf( "без навыка: %d\n", count( $no_skill ) );

foreach ( $no_skill as $title ) {
	echo "  · {$title}\n";
}

printf( "учебных без ступени: %d\n", count( $no_step ) );

foreach ( $no_step as $title ) {
	echo "  · {$title}\n";
}

$empty = get_terms( array( 'taxonomy' => 'skill', 'hide_empty' => false, 'parent' => 0, 'fields' => 'ids' ) );
$blank = array();

foreach ( get_terms( array( 'taxonomy' => 'skill', 'hide_empty' => false ) ) as $term ) {
	if ( in_array( $term->term_id, $empty, true ) ) {
		continue;
	}

	if ( 0 === (int) $term->count ) {
		$blank[] = $term->name;
	}
}

printf( "навыков без единой записи: %d", count( $blank ) );
echo $blank ? ' — ' . implode( ', ', $blank ) . "\n" : "\n";

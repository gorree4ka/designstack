<?php
/**
 * Число и слово в полях каталога согласуются: «192 страницы», «256 страниц», «161 страница».
 *
 * Поле «Длительность» у книг собиралось шаблоном «%d страниц», и шесть карточек партии 28.09.2026
 * вышли с «192 страниц», «384 страниц»; на странице тот же текст в оценке был написан верно.
 * Скрипт смотрит все опубликованные записи и печатает несогласованные пары.
 *
 *   wp eval-file scripts/check_plurals.php
 */

$ds_forms = array(
	'страница' => 'one',
	'страницы' => 'few',
	'страниц'  => 'many',
	'урок'     => 'one',
	'урока'    => 'few',
	'уроков'   => 'many',
	'час'      => 'one',
	'часа'     => 'few',
	'часов'    => 'many',
);
$ds_bad   = array();

foreach ( get_posts( array( 'post_type' => array( 'resource', 'post' ), 'post_status' => 'publish', 'numberposts' => -1 ) ) as $ds_post ) {
	$ds_texts = array( 'content' => $ds_post->post_content, 'excerpt' => $ds_post->post_excerpt );

	foreach ( array( 'duration', 'price_note', 'verdict', 'review_for', 'review_why', 'review_not' ) as $ds_key ) {
		$ds_texts[ $ds_key ] = (string) get_post_meta( $ds_post->ID, $ds_key, true );
	}

	foreach ( $ds_texts as $ds_key => $ds_text ) {
		if ( ! preg_match_all( '/(?<![\d.,])(\d+)\s+(' . implode( '|', array_keys( $ds_forms ) ) . ')(?![а-яё])/u', $ds_text, $ds_hits, PREG_SET_ORDER ) ) {
			continue;
		}

		foreach ( $ds_hits as $ds_hit ) {
			// После «около», «от», «до», «более» и им подобных нужен родительный падеж: «около 2 часов» — верно.
			$ds_before = mb_substr( $ds_text, 0, (int) mb_strpos( $ds_text, $ds_hit[0] ) );

			if ( preg_match( '/(?:около|от|до|более|менее|свыше|больше|меньше|порядка|из)\s*$/u', $ds_before ) ) {
				continue;
			}

			$ds_n    = (int) $ds_hit[1];
			$ds_two  = $ds_n % 100;
			$ds_one  = $ds_n % 10;
			$ds_want = ( $ds_two >= 11 && $ds_two <= 14 ) ? 'many' : ( 1 === $ds_one ? 'one' : ( $ds_one >= 2 && $ds_one <= 4 ? 'few' : 'many' ) );

			if ( $ds_forms[ $ds_hit[2] ] !== $ds_want ) {
				$ds_bad[] = "{$ds_post->post_name} · {$ds_key}: «{$ds_hit[0]}»";
			}
		}
	}
}

echo implode( "\n", $ds_bad ) . ( $ds_bad ? "\n" : '' ) . 'несогласованных пар: ' . count( $ds_bad ) . "\n";

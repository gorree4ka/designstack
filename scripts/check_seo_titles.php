<?php
/**
 * Заголовок для поиска не спорит с полями карточки (D198).
 *
 * Заголовок пишется руками и живёт дольше полей: цену или доступ из России проверили заново,
 * а строка в выдаче всё ещё обещает «бесплатный» или «недоступен из России». Скрипт сверяет
 * каждое такое слово с полем, из которого оно взято, и ещё — что заголовок есть у каждой
 * опубликованной карточки, начинается с названия и вместе с « — DesignStack» не длиннее 70 знаков.
 * Разделы и темы — та же длина с числом ресурсов.
 *
 *   wp eval-file scripts/check_seo_titles.php
 *
 * Запускать локально и на хостинге при каждом выкате, где менялись карточки.
 */

const DS_TITLE_MAX = 70;
const DS_BRAND     = ' — DesignStack';

// `wp eval-file` выполняет файл внутри функции: без `global` счётчик функции и счётчик файла —
// разные переменные, и скрипт печатал «проверок: 0» при ста шестидесяти карточках.
global $ds_checks, $ds_fails;

$ds_checks = 0;
$ds_fails  = array();

/**
 * Одна проверка: условие и что сказать, если не выполнено.
 *
 * @param string $where Чья строка.
 * @param bool   $ok    Условие.
 * @param string $why   Пояснение.
 */
function ds_check( string $where, bool $ok, string $why ): void {
	global $ds_checks, $ds_fails;

	++$ds_checks;

	if ( ! $ok ) {
		$ds_fails[] = $where . ' — ' . $why;
	}
}

$ds_ids = get_posts(
	array(
		'post_type'   => 'resource',
		'post_status' => 'publish',
		'numberposts' => -1,
		'fields'      => 'ids',
	)
);

// Кто кого называет аналогом: «аналог Miro» у sBoard честен, если у Miro в аналогах стоит sBoard.
$ds_listed = array();

foreach ( $ds_ids as $ds_id ) {
	foreach ( (array) get_post_meta( $ds_id, 'ru_alternative' ) as $ds_alt ) {
		$ds_listed[ (int) $ds_alt ] = true;
	}
}

foreach ( $ds_ids as $ds_id ) {
	$ds_slug  = get_post_field( 'post_name', $ds_id );
	$ds_title = trim( (string) get_post_meta( $ds_id, 'seo_title', true ) );
	$ds_f     = static fn( string $key ): string => (string) get_post_meta( $ds_id, $key, true );

	ds_check( $ds_slug, '' !== $ds_title, 'нет заголовка для поиска' );

	if ( '' === $ds_title ) {
		continue;
	}

	$ds_low  = mb_strtolower( $ds_title );
	$ds_name = trim( explode( ':', get_the_title( $ds_id ) )[0] );
	$ds_has  = static fn( string $word ): bool => false !== mb_strpos( $ds_low, $word );

	ds_check( $ds_slug, mb_strlen( $ds_title . DS_BRAND ) <= DS_TITLE_MAX, 'длина ' . mb_strlen( $ds_title . DS_BRAND ) );
	ds_check( $ds_slug, 0 === mb_strpos( $ds_title, $ds_name ), "не начинается с названия «{$ds_name}»" );
	ds_check( $ds_slug, ! preg_match( '/(^|\s)мы(\s|$)|лучш|vpn|топ-/u', $ds_low ), 'слово из запрета словаря' );

	$ds_rules = array(
		'бесплатн'       => array( 'free' === $ds_f( 'pricing' ), 'цена ' . $ds_f( 'pricing' ) ),
		'на русском'     => array( in_array( $ds_f( 'language' ), array( 'ru', 'multi' ), true ), 'язык ' . $ds_f( 'language' ) ),
		'на английском'  => array( in_array( $ds_f( 'language' ), array( 'en', 'multi' ), true ), 'язык ' . $ds_f( 'language' ) ),
		'российск'       => array( 'ru_native' === $ds_f( 'ru_payment' ) || false !== mb_stripos( $ds_f( 'verdict' ), 'российск' ), 'не ru_native и в вердикте не сказано' ),
		'кириллиц'       => array( in_array( $ds_f( 'cyrillic' ), array( 'yes', 'partial' ), true ), 'кириллица ' . $ds_f( 'cyrillic' ) ),
		'telegram'       => array( 'telegram' === $ds_f( 'platform' ), 'платформа ' . $ds_f( 'platform' ) ),
		'рассылк'        => array( 'newsletter' === $ds_f( 'platform' ), 'платформа ' . $ds_f( 'platform' ) ),
		'недоступ'       => array( 'blocked' === $ds_f( 'ru_open' ), 'доступ ' . $ds_f( 'ru_open' ) ),
		'и доступ'       => array( '' !== $ds_f( 'ru_open' ), 'нет поля доступа' ),
		'доступ из росс' => array( '' !== $ds_f( 'ru_open' ), 'нет поля доступа' ),
		'оплат'          => array( '' !== $ds_f( 'ru_payment' ), 'нет поля оплаты' ),
		'в рублях'       => array( 'ru_native' === $ds_f( 'ru_payment' ), 'оплата ' . $ds_f( 'ru_payment' ) ),
		'лиценз'         => array( '' !== $ds_f( 'license' ), 'нет поля лицензии' ),
		'закрыт'         => array( 'dead' === $ds_f( 'status' ), 'состояние ' . $ds_f( 'status' ) ),
		'книг'           => array( 'book' === $ds_f( 'format' ), 'формат ' . $ds_f( 'format' ) ),
		'подкаст'        => array( 'podcast' === $ds_f( 'format' ), 'формат ' . $ds_f( 'format' ) ),
		'курс'           => array( in_array( $ds_f( 'format' ), array( 'course', 'video', 'guide' ), true ), 'формат ' . $ds_f( 'format' ) ),
		'аналог'         => array( (bool) get_post_meta( $ds_id, 'ru_alternative' ) || isset( $ds_listed[ $ds_id ] ), 'пары нет в каталоге' ),
		'замен'          => array( (bool) get_post_meta( $ds_id, 'ru_alternative' ) || isset( $ds_listed[ $ds_id ] ) || false !== mb_stripos( $ds_f( 'verdict' ), 'замен' ), 'пары нет в каталоге и в вердикте' ),
	);

	foreach ( $ds_rules as $ds_word => $ds_rule ) {
		if ( $ds_has( $ds_word ) ) {
			ds_check( $ds_slug, $ds_rule[0], "«{$ds_word}» при: {$ds_rule[1]} · {$ds_title}" );
		}
	}
}

foreach ( array( 'resource_type', 'topic', 'category' ) as $ds_tax ) {
	foreach ( get_terms( array( 'taxonomy' => $ds_tax, 'hide_empty' => false ) ) as $ds_term ) {
		$ds_phrase = trim( (string) get_term_meta( $ds_term->term_id, 'seo_title', true ) );

		if ( '' === $ds_phrase ) {
			// Рубрики без заголовка остаются как были; разделы и темы каталога — все с ним.
			ds_check( $ds_tax . '/' . $ds_term->slug, 'category' === $ds_tax || ! $ds_term->count, 'нет заголовка для поиска' );
			continue;
		}

		$ds_full = 'category' === $ds_tax ? $ds_phrase : $ds_phrase . ': ' . designstack_core_count_line( max( (int) $ds_term->count, 100 ) );
		ds_check( $ds_tax . '/' . $ds_term->slug, mb_strlen( $ds_full . DS_BRAND ) <= DS_TITLE_MAX, 'длина с трёхзначным числом ' . mb_strlen( $ds_full . DS_BRAND ) );
	}
}

foreach ( $ds_fails as $ds_line ) {
	echo '  ✘ ' . $ds_line . "\n";
}

printf( "карточек: %d, проверок: %d, провалов: %d\n", count( $ds_ids ), $ds_checks, count( $ds_fails ) );

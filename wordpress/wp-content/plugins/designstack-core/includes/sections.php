<?php
/**
 * Разделы каталога: названия, счётчики, порядок архива и крошки.
 *
 * Термин `resource_type` зовётся в единственном числе — так он подписывает тип в карточке
 * («Инструмент»). Раздел называется иначе: «Инструменты», «Учёба», «Ассеты», «Сообщества».
 * Это разные слова, а не число, поэтому заголовок архива и крошки берут название отсюда,
 * а не из термина (решение t1 листа партии 1, 12.09.2026).
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Разделы каталога: слаг типа → название раздела и строка под ним.
 *
 * @return array<string, array{name: string, note: string}>
 */
function designstack_core_type_sections(): array {
	return array(
		'tool'      => array(
			'name' => __( 'Инструменты', 'designstack-core' ),
			'note' => __( 'Редакторы, прототипы, тесты', 'designstack-core' ),
		),
		'learning'  => array(
			'name' => __( 'Учёба', 'designstack-core' ),
			'note' => __( 'Курсы, книги, статьи, видео', 'designstack-core' ),
		),
		'asset'     => array(
			'name' => __( 'Ассеты', 'designstack-core' ),
			'note' => __( 'UI-киты, шрифты, иконки, мокапы', 'designstack-core' ),
		),
		'community' => array(
			'name' => __( 'Сообщества', 'designstack-core' ),
			'note' => __( 'Каналы, чаты, вакансии', 'designstack-core' ),
		),
	);
}

/**
 * Название раздела по слагу типа.
 *
 * @param string $type Слаг типа.
 * @return string Пусто, если тип неизвестен.
 */
function designstack_core_section_name( string $type ): string {
	$sections = designstack_core_type_sections();

	return isset( $sections[ $type ] ) ? $sections[ $type ]['name'] : '';
}

/**
 * Форма слова по числу: 1 ресурс, 2 ресурса, 5 ресурсов.
 *
 * @param int                      $number Число.
 * @param array{0: string, 1: string, 2: string} $forms  Формы для 1, 2 и 5.
 * @return string
 */
function designstack_core_plural( int $number, array $forms ): string {
	$number = abs( $number ) % 100;
	$tail   = $number % 10;

	if ( $number > 10 && $number < 20 ) {
		return $forms[2];
	}

	if ( $tail > 1 && $tail < 5 ) {
		return $forms[1];
	}

	return 1 === $tail ? $forms[0] : $forms[2];
}

/**
 * Строка выдачи: «7 ресурсов».
 *
 * @param int $number Число записей.
 * @return string
 */
function designstack_core_count_line( int $number ): string {
	return sprintf(
		'%1$d %2$s',
		$number,
		designstack_core_plural(
			$number,
			array(
				__( 'ресурс', 'designstack-core' ),
				__( 'ресурса', 'designstack-core' ),
				__( 'ресурсов', 'designstack-core' ),
			)
		)
	);
}

/**
 * Термин текущего архива каталога.
 *
 * @return WP_Term|null
 */
function designstack_core_archive_term(): ?WP_Term {
	if ( ! is_tax( array( 'resource_type', 'topic' ) ) && ! is_category() ) {
		return null;
	}

	$term = get_queried_object();

	return $term instanceof WP_Term ? $term : null;
}

/**
 * Заголовок текущего архива: название раздела или темы.
 *
 * @return string
 */
function designstack_core_archive_title(): string {
	$term = designstack_core_archive_term();

	if ( ! $term ) {
		return '';
	}

	if ( 'resource_type' === $term->taxonomy ) {
		$section = designstack_core_section_name( $term->slug );

		return $section ? $section : $term->name;
	}

	return $term->name;
}

/**
 * Строка выдачи архива: ресурсы в каталоге, записи в разделах редакции.
 *
 * @param int $number Число записей.
 * @return string
 */
function designstack_core_archive_count_line( int $number ): string {
	if ( ! is_category() ) {
		return designstack_core_count_line( $number );
	}

	$term = get_queried_object();

	return sprintf(
		'%1$d %2$s',
		$number,
		designstack_core_plural(
			$number,
			designstack_core_entry_forms( $term instanceof WP_Term ? $term->slug : '' )
		)
	);
}

/*
 * Порядок каталога по умолчанию — сначала недавно проверенные (D40) — переехал
 * в includes/filters.php вместе с фильтрами и местом закрытых ресурсов (этап 14):
 * порядок и выборка задаются одним хуком, иначе они спорят за orderby.
 */

/**
 * Крошки: звено раздела подписывается названием раздела, а не термина.
 *
 * @param array<int, array<string, mixed>> $items Звенья пути.
 * @return array<int, array<string, mixed>>
 */
function designstack_core_breadcrumb_items( array $items ): array {
	$names = array();

	foreach ( designstack_core_type_sections() as $slug => $section ) {
		$term = get_term_by( 'slug', $slug, 'resource_type' );

		if ( $term instanceof WP_Term ) {
			$names[ $term->name ] = $section['name'];
		}
	}

	foreach ( $items as $index => $item ) {
		$label = isset( $item['label'] ) ? (string) $item['label'] : '';

		if ( isset( $names[ $label ] ) ) {
			$items[ $index ]['label'] = $names[ $label ];
		}
	}

	// Служебные страницы ядро подписывает по-своему: «Результаты поиска для "figma"»,
	// «Страница не найдена». На странице заголовки другие, а одно понятие называется одним словом.
	if ( $items && ( is_search() || is_404() ) ) {
		$last = array_key_last( $items );

		$items[ $last ]['label'] = is_search()
			? __( 'Поиск', 'designstack-core' )
			: __( 'Такой страницы нет', 'designstack-core' );
	}

	return $items;
}
add_filter( 'block_core_breadcrumbs_items', 'designstack_core_breadcrumb_items' );

/**
 * Заголовок вкладки: у раздела каталога то же название, что в H1 и крошках.
 *
 * Без этого во вкладке стоит имя термина в единственном числе — «Инструмент», — а на странице
 * заголовок «Инструменты»: одна страница называется двумя способами.
 *
 * @param array<string, string> $parts Части заголовка.
 * @return array<string, string>
 */
function designstack_core_document_title( array $parts ): array {
	$title = designstack_core_archive_title();

	if ( '' !== $title ) {
		$parts['title'] = $title;
	}

	return $parts;
}
add_filter( 'document_title_parts', 'designstack_core_document_title' );

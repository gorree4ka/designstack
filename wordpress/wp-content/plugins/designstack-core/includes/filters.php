<?php
/**
 * Фильтры, сортировка и порядок выдачи архивов.
 *
 * Значения приходят адресом: `/tools/?pricing=free,freemium&ru_open=open`. Несколько значений —
 * через запятую (решение этапа 14); форма без JavaScript отдаёт длинный вид `pricing[]=…`,
 * он тоже понимается. Чужое значение игнорируется и в выдачу не попадает — 404 из-за опечатки
 * в параметре не бывает.
 *
 * Темы и типы WordPress фильтрует сам: `topic` и `resource_type` — публичные таксономии со своими
 * переменными запроса, и здесь они не дублируются (проба этапа 14). Грейд закрыт от запросов,
 * поэтому его добавляем руками.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Оси фильтров: откуда берётся значение и чем оно проверяется.
 *
 * @return array<string, array{source: string, enum: string}>
 */
function designstack_core_filter_map(): array {
	return array(
		'pricing'     => array( 'source' => 'meta', 'enum' => 'pricing' ),
		'ru_open'     => array( 'source' => 'meta', 'enum' => 'ru_open' ),
		'ru_payment'  => array( 'source' => 'meta', 'enum' => 'ru_payment' ),
		'platforms'   => array( 'source' => 'meta', 'enum' => 'platforms' ),
		'format'      => array( 'source' => 'meta', 'enum' => 'format' ),
		'language'    => array( 'source' => 'meta', 'enum' => 'language' ),
		'license'     => array( 'source' => 'meta', 'enum' => 'license' ),
		'cyrillic'    => array( 'source' => 'meta', 'enum' => 'cyrillic' ),
		'platform'    => array( 'source' => 'meta', 'enum' => 'platform' ),
		'file_format' => array( 'source' => 'meta', 'enum' => 'file_format' ),
		'is_jobs'     => array( 'source' => 'meta', 'enum' => 'is_jobs' ),
		'topic'       => array( 'source' => 'taxonomy', 'enum' => 'topic' ),
		'level'       => array( 'source' => 'taxonomy', 'enum' => 'level' ),
	);
}

/**
 * Допустимые значения оси: слаг → подпись из словаря.
 *
 * @param string $key Ось фильтра.
 * @return array<string, string>
 */
function designstack_core_filter_options( string $key ): array {
	$map = designstack_core_filter_map();

	if ( ! isset( $map[ $key ] ) ) {
		return array();
	}

	if ( 'taxonomy' === $map[ $key ]['source'] ) {
		$terms = get_terms(
			array(
				'taxonomy'   => $key,
				'hide_empty' => true,
			)
		);

		if ( is_wp_error( $terms ) ) {
			return array();
		}

		$out = array();

		foreach ( $terms as $term ) {
			$out[ $term->slug ] = $term->name;
		}

		return $out;
	}

	if ( 'file_format' === $key ) {
		$options = array();

		// В записи формат лежит слагом («otf»), в подписи — как пишут люди («OTF»):
		// сравнивать надо слагом, иначе выборка держится на регистре в базе.
		foreach ( designstack_core_file_formats() as $format ) {
			$options[ strtolower( $format ) ] = $format;
		}

		return $options;
	}

	if ( 'is_jobs' === $key ) {
		return array( '1' => __( 'есть', 'designstack-core' ) );
	}

	$enums = designstack_core_enums();

	return $enums[ $map[ $key ]['enum'] ] ?? array();
}

/**
 * Значения оси из адреса: через запятую или массивом из формы.
 *
 * @param string $key Ось фильтра.
 * @return array<int, string> Только известные значения.
 */
function designstack_core_filter_request( string $key ): array {
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- чтение фильтров из адреса, не действие.
	$raw = $_GET[ $key ] ?? '';

	if ( is_array( $raw ) ) {
		$values = array_map( 'strval', $raw );
	} else {
		$values = explode( ',', (string) $raw );
	}

	$values  = array_filter( array_map( 'trim', array_map( 'sanitize_text_field', array_map( 'wp_unslash', $values ) ) ) );
	$allowed = designstack_core_filter_options( $key );
	$out     = array();

	foreach ( $values as $value ) {
		foreach ( array_keys( $allowed ) as $option ) {
			if ( 0 === strcasecmp( (string) $option, $value ) && ! in_array( (string) $option, $out, true ) ) {
				$out[] = (string) $option;
			}
		}
	}

	return $out;
}

/**
 * Все активные фильтры текущей страницы.
 *
 * Тема и тип, взятые из адреса самой страницы (`/topic/prototyping/`), фильтрами не считаются:
 * снимать их чипсом нечего, это и есть страница.
 *
 * @return array<string, array<int, string>>
 */
function designstack_core_active_filters(): array {
	$active = array();
	$term   = function_exists( 'designstack_core_archive_term' ) ? designstack_core_archive_term() : null;

	foreach ( array_keys( designstack_core_filter_map() ) as $key ) {
		if ( $term && $key === $term->taxonomy ) {
			continue;
		}

		$values = designstack_core_filter_request( $key );

		if ( $values ) {
			$active[ $key ] = $values;
		}
	}

	// Тип ресурса — ось страницы темы и выдачи поиска (US-10).
	if ( ! $term || 'resource_type' !== $term->taxonomy ) {
		$type = designstack_core_filter_request_type();

		if ( $type ) {
			$active['resource_type'] = $type;
		}
	}

	return $active;
}

/**
 * Значения оси типа ресурса из адреса.
 *
 * @return array<int, string>
 */
function designstack_core_filter_request_type(): array {
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- чтение фильтра из адреса.
	$raw    = (string) ( $_GET['resource_type'] ?? '' );
	$values = array_filter( array_map( 'sanitize_key', explode( ',', $raw ) ) );
	$out    = array();

	foreach ( $values as $value ) {
		if ( term_exists( $value, 'resource_type' ) && ! in_array( $value, $out, true ) ) {
			$out[] = $value;
		}
	}

	return $out;
}

/**
 * Порядок выдачи: слаг → подпись.
 *
 * @return array<string, string>
 */
function designstack_core_sort_options(): array {
	return array(
		'checked' => __( 'Сначала проверенные', 'designstack-core' ),
		'title'   => __( 'По названию', 'designstack-core' ),
		'new'     => __( 'Сначала новые', 'designstack-core' ),
	);
}

/**
 * Выбранный порядок выдачи.
 *
 * @return string
 */
function designstack_core_current_sort(): string {
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- чтение порядка из адреса.
	$sort = sanitize_key( (string) ( $_GET['sort'] ?? '' ) );

	return isset( designstack_core_sort_options()[ $sort ] ) ? $sort : 'checked';
}

/**
 * Адрес текущего архива без параметров.
 *
 * @return string
 */
function designstack_core_archive_base(): string {
	$term = function_exists( 'designstack_core_archive_term' ) ? designstack_core_archive_term() : null;

	if ( $term ) {
		return (string) get_term_link( $term );
	}

	if ( is_search() ) {
		return home_url( '/search/' );
	}

	return home_url( '/' );
}

/**
 * Адрес с набором фильтров и порядком.
 *
 * @param array<string, array<int, string>> $filters Фильтры.
 * @param string                            $sort    Порядок или ''.
 * @return string
 */
function designstack_core_filter_url( array $filters, string $sort = '' ): string {
	$args = array();

	foreach ( $filters as $key => $values ) {
		if ( $values ) {
			$args[ $key ] = implode( ',', $values );
		}
	}

	if ( $sort && 'checked' !== $sort ) {
		$args['sort'] = $sort;
	}

	if ( is_search() ) {
		$args['s'] = get_search_query();
	}

	$base = designstack_core_archive_base();

	return $args ? add_query_arg( $args, $base ) : $base;
}

/**
 * Части выборки по полям записи.
 *
 * @param array<string, array<int, string>> $active Активные фильтры.
 * @return array<int|string, mixed>
 */
function designstack_core_meta_clauses( array $active ): array {
	$map     = designstack_core_filter_map();
	$clauses = array();

	foreach ( $active as $key => $values ) {
		if ( ! isset( $map[ $key ] ) || 'meta' !== $map[ $key ]['source'] ) {
			continue;
		}

		$clause = array(
			'key'     => $key,
			'value'   => $values,
			'compare' => 'IN',
		);

		// «На русском» и «На английском» включают двуязычные ресурсы: они подходят под оба выбора (US-12).
		if ( 'language' === $key && array_intersect( array( 'ru', 'en' ), $values ) ) {
			$values          = array_values( array_unique( array_merge( $values, array( 'multi' ) ) ) );
			$clause['value'] = $values;
		}

		// «Оплачивается из РФ» включает бесплатные: платить нечего, и поля оплаты у них нет (D28).
		if ( 'ru_payment' === $key && in_array( 'payable', $values, true ) ) {
			$clause = array(
				'relation' => 'OR',
				$clause,
				array(
					'key'   => 'pricing',
					'value' => 'free',
				),
			);
		}

		$clauses[] = $clause;
	}

	return $clauses;
}

/**
 * Фильтры, порядок и место закрытых ресурсов в главном запросе архива.
 *
 * @param WP_Query $query Запрос.
 * @return void
 */
function designstack_core_filter_main_query( WP_Query $query ): void {
	if ( is_admin() || ! $query->is_main_query() ) {
		return;
	}

	if ( ! $query->is_tax( array( 'resource_type', 'topic' ) ) ) {
		return;
	}

	$active = designstack_core_active_filters();

	// Грейд закрыт от запросов, поэтому WordPress сам его не применит.
	if ( ! empty( $active['level'] ) ) {
		$tax = (array) $query->get( 'tax_query' );

		$tax[] = array(
			'taxonomy' => 'level',
			'field'    => 'slug',
			'terms'    => $active['level'],
		);

		if ( count( $tax ) > 1 ) {
			$tax['relation'] = 'AND';
		}

		$query->set( 'tax_query', $tax );
	}

	$meta = designstack_core_meta_clauses( $active );

	// Две именованные части нужны порядку: живое сверху, закрытое в конец.
	$meta['ds_state']   = array(
		'key'     => 'status',
		'compare' => 'EXISTS',
	);
	$meta['ds_checked'] = array(
		'key'     => 'checked_at',
		'compare' => 'EXISTS',
	);
	$meta['relation']   = 'AND';

	$query->set( 'meta_query', $meta );

	switch ( designstack_core_current_sort() ) {
		case 'title':
			$query->set( 'orderby', array( 'ds_state' => 'ASC', 'title' => 'ASC' ) );
			break;

		case 'new':
			$query->set( 'orderby', array( 'ds_state' => 'ASC', 'date' => 'DESC' ) );
			break;

		default:
			$query->set( 'orderby', array( 'ds_state' => 'ASC', 'ds_checked' => 'DESC' ) );
	}
}
add_action( 'pre_get_posts', 'designstack_core_filter_main_query' );

/**
 * Канонический адрес архива с фильтрами — сам архив без параметров (US-16).
 *
 * @param string $url Адрес.
 * @return string
 */
function designstack_core_canonical( $url ) {
	if ( ! is_tax( array( 'resource_type', 'topic' ) ) ) {
		return $url;
	}

	$active = designstack_core_active_filters();

	// Страница с одним фильтром — самостоятельный ответ на запрос, поэтому canonical
	// на себя; с двумя и больше — почти дубль архива, каноникализируем на него (D120).
	if ( 1 === count( $active ) && 'checked' === designstack_core_current_sort() ) {
		return designstack_core_filter_url( $active );
	}

	return $active || 'checked' !== designstack_core_current_sort()
		? designstack_core_archive_base()
		: $url;
}
add_filter( 'get_canonical_url', 'designstack_core_canonical' );
add_filter( 'wpseo_canonical', 'designstack_core_canonical' );

/**
 * Что закрываем от индексации: выдачу поиска, пустые выборки и глубокие комбинации фильтров.
 *
 * @param array<string, mixed> $robots Правила.
 * @return array<string, mixed>
 */
function designstack_core_robots( array $robots ): array {
	global $wp_query;

	if ( is_search() ) {
		$robots['noindex'] = true;

		return $robots;
	}

	if ( ! is_tax( array( 'resource_type', 'topic' ) ) ) {
		return $robots;
	}

	$active = designstack_core_active_filters();

	// Один фильтр — готовая посадочная страница под живой запрос, два и больше —
	// почти одинаковые страницы, за которые поисковики понижают сайт целиком (D120).
	if ( ! $wp_query->found_posts || count( $active ) > 1 ) {
		$robots['noindex'] = true;
	}

	return $robots;
}
add_filter( 'wp_robots', 'designstack_core_robots' );

/**
 * Канонический адрес в шапке документа: на архивах ядро его не печатает.
 *
 * @return void
 */
function designstack_core_canonical_link(): void {
	// Главная: ядро печатает canonical только для одиночных записей, а страница
	// со списком остаётся без него — и адреса с метками выглядят как разные страницы.
	if ( is_front_page() ) {
		printf( '<link rel="canonical" href="%s">' . "\n", esc_url( home_url( '/' ) ) );

		return;
	}

	if ( ! is_tax( array( 'resource_type', 'topic' ) ) && ! is_category() ) {
		return;
	}

	$active = is_category() ? array() : designstack_core_active_filters();
	$base   = is_category() ? (string) get_term_link( get_queried_object() ) : designstack_core_archive_base();

	if ( 1 === count( $active ) && 'checked' === designstack_core_current_sort() ) {
		$base = designstack_core_filter_url( $active );
	}

	$page = max( 1, (int) get_query_var( 'paged' ) );

	// Страница выдачи каноникализируется на себя, фильтры и порядок — на чистый архив (US-16).
	if ( $page > 1 ) {
		$base = (string) get_pagenum_link( $page );
	}

	printf( '<link rel="canonical" href="%s">' . "
", esc_url( $base ) );
}
add_action( 'wp_head', 'designstack_core_canonical_link', 9 );

/**
 * Ссылки на соседние страницы выдачи в шапке документа (US-20).
 *
 * @return void
 */
function designstack_core_pagination_links(): void {
	global $wp_query;

	if ( ! is_tax( array( 'resource_type', 'topic' ) ) && ! is_category() ) {
		return;
	}

	$total   = (int) $wp_query->max_num_pages;
	$current = max( 1, (int) get_query_var( 'paged' ) );

	if ( $total < 2 ) {
		return;
	}

	if ( $current > 1 ) {
		printf( '<link rel="prev" href="%s">' . "\n", esc_url( (string) get_pagenum_link( $current - 1 ) ) );
	}

	if ( $current < $total ) {
		printf( '<link rel="next" href="%s">' . "\n", esc_url( (string) get_pagenum_link( $current + 1 ) ) );
	}
}
add_action( 'wp_head', 'designstack_core_pagination_links' );

/**
 * Значения полей, которые вообще есть у опубликованных ресурсов раздела.
 *
 * Панель не показывает значение, под которое нет ни одного ресурса (US-14): выбор,
 * который заведомо даёт ноль, — это ловушка. Считается одним запросом на раздел
 * и живёт час в транзиенте; сбрасывается при правке ресурса или термина.
 *
 * @param string $type Слаг типа ресурса.
 * @return array<string, array<int, string>> Ось → значения.
 */
function designstack_core_available_values( string $type ): array {
	$key   = 'designstack_core_values_' . $type;
	$cache = get_transient( $key );

	if ( is_array( $cache ) ) {
		return $cache;
	}

	$posts = get_posts(
		array(
			'post_type'      => 'resource',
			'post_status'    => 'publish',
			'posts_per_page' => -1,
			'fields'         => 'ids',
			'no_found_rows'  => true,
			'tax_query'      => array(
				array(
					'taxonomy' => 'resource_type',
					'field'    => 'slug',
					'terms'    => $type,
				),
			),
		)
	);

	$values = array();

	foreach ( designstack_core_filter_map() as $axis => $data ) {
		if ( 'meta' !== $data['source'] ) {
			continue;
		}

		$values[ $axis ] = array();
	}

	foreach ( $posts as $post_id ) {
		foreach ( array_keys( $values ) as $axis ) {
			foreach ( (array) get_post_meta( $post_id, $axis ) as $value ) {
				$value = (string) $value;

				if ( '' !== $value && ! in_array( $value, $values[ $axis ], true ) ) {
					$values[ $axis ][] = $value;
				}
			}
		}
	}

	set_transient( $key, $values, HOUR_IN_SECONDS );

	return $values;
}

/**
 * Сбрасывает разобранные значения фильтров.
 *
 * @return void
 */
function designstack_core_flush_values(): void {
	foreach ( array_keys( designstack_core_type_sections() ) as $type ) {
		delete_transient( 'designstack_core_values_' . $type );
	}
}
add_action( 'save_post_resource', 'designstack_core_flush_values' );
add_action( 'deleted_post', 'designstack_core_flush_values' );
add_action( 'edited_term', 'designstack_core_flush_values' );
add_action( 'delete_term', 'designstack_core_flush_values' );

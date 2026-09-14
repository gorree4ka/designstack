<?php
/**
 * Разметка главной: поиск, подборка для старта, проверенное за неделю, свежие подборки, подписка.
 *
 * Классы повторяют каталог паттернов (`docs/ds/components.md`). Секции, для которых нет данных,
 * не выводятся целиком — так записано в `docs/ia/wireframes/home.md`, раздел «Пустое состояние».
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Секция страницы: заголовок, строка под ним, содержимое и ссылка «все».
 *
 * @param string $title Заголовок.
 * @param string $sub   Строка под заголовком или ''.
 * @param string $body  Содержимое.
 * @param string $more  Разметка ссылки «все» или ''.
 * @return string
 */
function designstack_core_section( string $title, string $sub, string $body, string $more = '' ): string {
	if ( '' === $body ) {
		return '';
	}

	$head = sprintf( '<h2 class="ds-section__title">%s</h2>', esc_html( $title ) );

	if ( '' !== $sub ) {
		$head .= sprintf( '<p class="ds-section__sub">%s</p>', esc_html( $sub ) );
	}

	return sprintf(
		'<section class="ds-section"><div class="ds-section__head">%1$s</div><div class="ds-section__body">%2$s</div>%3$s</section>',
		$head,
		$body,
		$more ? sprintf( '<div class="ds-section__more">%s</div>', $more ) : ''
	);
}

/**
 * Отдельная ссылка «все» с шевроном.
 *
 * @param string $url   Адрес.
 * @param string $label Подпись из словаря.
 * @return string
 */
function designstack_core_more_link( string $url, string $label ): string {
	return sprintf(
		'<a class="ds-link ds-link--standalone" href="%1$s">%2$s%3$s</a>',
		esc_url( $url ),
		esc_html( $label ),
		designstack_core_icon( 'chevron-right' )
	);
}

/**
 * Форма поиска по каталогу.
 *
 * @param string $variant header | home | results.
 * @return string
 */
function designstack_core_render_search( string $variant = 'home' ): string {
	$variant = in_array( $variant, array( 'header', 'home', 'results' ), true ) ? $variant : 'home';
	$id      = 'ds-search-' . $variant;
	$button  = 'home' === $variant
		? 'ds-button ds-button--primary ds-button--lg'
		: 'ds-button ds-button--secondary';

	return sprintf(
		'<form class="ds-search ds-search--%1$s" role="search" method="get" action="%2$s">'
		. '<label class="screen-reader-text" for="%3$s">%4$s</label>'
		. '<input class="ds-search__field" id="%3$s" type="search" name="s" placeholder="%4$s" value="%5$s">'
		. '<button type="submit" class="%6$s">%7$s</button></form>',
		esc_attr( $variant ),
		esc_url( home_url( '/search/' ) ),
		esc_attr( $id ),
		esc_attr__( 'Поиск по каталогу', 'designstack-core' ),
		esc_attr( 'results' === $variant ? get_search_query() : '' ),
		esc_attr( $button ),
		esc_html__( 'Найти', 'designstack-core' )
	);
}

/**
 * Шаги подборки для старта: номер, название шага и тема каталога.
 *
 * Шаг «Тест» из вайрфрейма не заводится: отдельной темы для тестов в каталоге нет,
 * тесты лежат в теме UX-исследований (решение h11, апрув в чате 12.09.2026).
 *
 * @return array<int, array{title: string, topic: string}>
 */
function designstack_core_starter_steps(): array {
	return array(
		array(
			'title' => __( '1. Исследование', 'designstack-core' ),
			'topic' => 'ux-research',
		),
		array(
			'title' => __( '2. Прототип', 'designstack-core' ),
			'topic' => 'prototyping',
		),
		array(
			'title' => __( '3. Интерфейс', 'designstack-core' ),
			'topic' => 'ui-visual',
		),
		array(
			'title' => __( '4. Портфолио', 'designstack-core' ),
			'topic' => 'career-portfolio',
		),
	);
}

/**
 * Подборка для старта: четыре шага по три карточки.
 *
 * @return string
 */
function designstack_core_render_starter(): string {
	$steps = '';
	// Ресурс попадает в подборку один раз: темы пересекаются, и без этого одна
	// карточка встаёт сразу в двух шагах.
	$used = array();

	foreach ( designstack_core_starter_steps() as $step ) {
		$posts = get_posts(
			array(
				'post_type'      => 'resource',
				'post_status'    => 'publish',
				'post__not_in'   => $used,
				'posts_per_page' => 3,
				'no_found_rows'  => true,
				'meta_key'       => 'checked_at',
				'orderby'        => 'meta_value',
				'order'          => 'DESC',
				// Подпись секции обещает бесплатное и проверенное, поэтому выборка это и проверяет:
				// платный без бесплатного тарифа, закрытый из России и снятый с публикации сюда не попадают.
				// Иначе первый экран для новичка отправляет его туда, куда он не сможет зайти.
				'meta_query'     => array(
					'relation' => 'AND',
					array(
						'key'     => 'pricing',
						'value'   => array( 'free', 'freemium' ),
						'compare' => 'IN',
					),
					array(
						'key'   => 'ru_open',
						'value' => 'open',
					),
					array(
						'key'   => 'status',
						'value' => 'active',
					),
				),
				'tax_query'      => array(
					'relation' => 'AND',
					array(
						'taxonomy' => 'topic',
						'field'    => 'slug',
						'terms'    => $step['topic'],
					),
					array(
						'taxonomy' => 'level',
						'field'    => 'slug',
						'terms'    => 'junior',
					),
				),
			)
		);

		if ( ! $posts ) {
			continue;
		}

		$cards = '';

		foreach ( $posts as $post ) {
			$used[]  = (int) $post->ID;
			// У секции свой H2, у шага H3 — карточка идёт следующей ступенью.
			$cards  .= designstack_core_render_card( (int) $post->ID, 4 );
		}

		$steps .= sprintf(
			'<div class="ds-steps__step"><h3 class="ds-steps__title">%1$s</h3>'
			. '<div class="ds-resource-list ds-resource-list--column">%2$s</div></div>',
			esc_html( $step['title'] ),
			$cards
		);
	}

	if ( '' === $steps ) {
		return '';
	}

	return designstack_core_section(
		__( 'Подборка для старта', 'designstack-core' ),
		__( 'Ресурсы для Junior по шагам учебной задачи — от исследования до портфолио. Всё бесплатно или с бесплатным тарифом и открывается из России.', 'designstack-core' ),
		sprintf( '<div class="ds-steps">%s</div>', $steps )
	);
}

/**
 * Проверено на этой неделе: ресурсы с датой проверки за последние 7 дней.
 *
 * @return string
 */
function designstack_core_render_checked_week(): string {
	$posts = get_posts(
		array(
			'post_type'      => 'resource',
			'post_status'    => 'publish',
			'posts_per_page' => 6,
			'no_found_rows'  => true,
			'meta_key'       => 'checked_at',
			'orderby'        => 'meta_value',
			'order'          => 'DESC',
			'meta_query'     => array(
				array(
					'key'     => 'checked_at',
					'value'   => gmdate( 'Y-m-d', strtotime( '-7 days', (int) current_time( 'timestamp' ) ) ),
					'compare' => '>=',
					'type'    => 'DATE',
				),
			),
		)
	);

	if ( ! $posts ) {
		return '';
	}

	$cards = '';

	foreach ( $posts as $post ) {
		$cards .= designstack_core_render_card( (int) $post->ID );
	}

	return designstack_core_section(
		__( 'Проверено на этой неделе', 'designstack-core' ),
		__( 'Эти записи мы пересмотрели за последнюю неделю', 'designstack-core' ),
		sprintf( '<div class="ds-resource-list ds-resource-list--grid">%s</div>', $cards )
	);
}

/**
 * Сколько опубликованных ресурсов стоит в записи: считает блоки «список ресурсов».
 *
 * @param int $post_id Идентификатор записи.
 * @return int
 */
function designstack_core_count_resources( int $post_id ): int {
	$post = get_post( $post_id );

	if ( ! $post ) {
		return 0;
	}

	$ids = array();

	foreach ( parse_blocks( $post->post_content ) as $block ) {
		if ( 'designstack/resource-list' !== ( $block['blockName'] ?? '' ) ) {
			continue;
		}

		foreach ( (array) ( $block['attrs']['ids'] ?? array() ) as $id ) {
			$id = absint( $id );

			if ( $id ) {
				$ids[ $id ] = true;
			}
		}
	}

	if ( ! $ids ) {
		return 0;
	}

	// Один запрос на все записи вместо запроса на каждую: статус читается уже из кеша.
	_prime_post_caches( array_keys( $ids ), false, false );

	$published = 0;

	foreach ( array_keys( $ids ) as $id ) {
		if ( 'publish' === get_post_status( $id ) ) {
			$published++;
		}
	}

	return $published;
}

/**
 * Карточка записи: подборка, выпуск, обзор.
 *
 * @param int  $post_id   Идентификатор записи.
 * @param bool $with_kind Показывать вид записи.
 * @param int  $level     Уровень заголовка, 2..4: в архиве карточка идёт под H1, в секции — под её H2.
 * @return string
 */
function designstack_core_render_post_card( int $post_id, bool $with_kind = false, int $level = 3 ): string {
	$post = get_post( $post_id );

	if ( ! $post ) {
		return '';
	}

	$count = designstack_core_count_resources( $post_id );
	$meta  = array();

	// В выдаче поиска у каждой записи виден её вид: подборка, выпуск или обзор (US-22).
	if ( $with_kind ) {
		$kinds = array(
			'collections' => __( 'Подборка', 'designstack-core' ),
			'digest'      => __( 'Выпуск дайджеста', 'designstack-core' ),
			'reviews'     => __( 'Обзор', 'designstack-core' ),
		);
		$kind  = $kinds[ designstack_core_entry_category( $post_id ) ] ?? __( 'Страница', 'designstack-core' );

		$meta[] = $kind;
	}

	if ( $count ) {
		$meta[] = sprintf(
			'%1$d %2$s',
			$count,
			designstack_core_plural(
				$count,
				array(
					__( 'ресурс', 'designstack-core' ),
					__( 'ресурса', 'designstack-core' ),
					__( 'ресурсов', 'designstack-core' ),
				)
			)
		);
	}

	// Месяц строчной буквой и неразрывный пробел после числа — как в дате проверки.
	$time   = (int) get_post_time( 'U', false, $post_id );
	$meta[] = date_i18n( 'j', $time ) . "\u{00A0}" . mb_strtolower( date_i18n( 'M', $time ) ) . ' ' . date_i18n( 'Y', $time );

	$excerpt = get_the_excerpt( $post_id );
	$desc    = $excerpt ? sprintf( '<p class="ds-post-card__desc">%s</p>', esc_html( $excerpt ) ) : '';

	return sprintf(
		'<article class="ds-post-card"><%1$s class="ds-post-card__title">'
		. '<a class="ds-post-card__link" href="%2$s">%3$s</a></%1$s>%4$s'
		. '<p class="ds-meta ds-post-card__meta">%5$s</p></article>',
		'h' . min( 4, max( 2, $level ) ),
		esc_url( (string) get_permalink( $post_id ) ),
		esc_html( get_the_title( $post_id ) ),
		$desc,
		esc_html( designstack_core_join( $meta ) )
	);
}

/**
 * Свежие подборки: до трёх последних записей категории.
 *
 * @param string $category Слаг категории.
 * @param string $title    Заголовок секции.
 * @param string $label    Подпись ссылки «все».
 * @param int    $exclude  Какую запись пропустить.
 * @return string
 */
function designstack_core_render_post_list( string $category, string $title, string $label, int $exclude = 0 ): string {
	$term = get_category_by_slug( $category );

	if ( ! $term ) {
		return '';
	}

	$posts = get_posts(
		array(
			'post_type'      => 'post',
			'post_status'    => 'publish',
			'posts_per_page' => 3,
			'no_found_rows'  => true,
			'cat'            => $term->term_id,
			'exclude'        => $exclude ? array( $exclude ) : array(),
		)
	);

	if ( ! $posts ) {
		return '';
	}

	$cards = '';

	foreach ( $posts as $post ) {
		$cards .= designstack_core_render_post_card( (int) $post->ID );
	}

	return designstack_core_section(
		$title,
		'',
		sprintf( '<div class="ds-post-list">%s</div>', $cards ),
		designstack_core_more_link( (string) get_category_link( $term ), $label )
	);
}

/**
 * Адрес Telegram-канала дайджеста.
 *
 * Канала пока нет (O5): опция пуста, и блок подписки не выводится ни на главной,
 * ни в выпуске, ни в подвале — так записано в вайрфреймах.
 *
 * @return string
 */
function designstack_core_channel_url(): string {
	return (string) get_option( 'designstack_core_channel', '' );
}

/**
 * Блок подписки на дайджест.
 *
 * @param string $variant block | footer.
 * @return string
 */
function designstack_core_render_subscribe( string $variant = 'block', string $only_category = '' ): string {
	$url = designstack_core_channel_url();

	if ( '' === $url ) {
		return '';
	}

	// Блок подписки стоит на главной и на выпусках; на подборке его нет (US-43).
	if ( '' !== $only_category ) {
		if ( ! is_singular( 'post' ) || $only_category !== designstack_core_entry_category( (int) get_queried_object_id() ) ) {
			return '';
		}
	}

	$button = sprintf(
		'<div class="ds-subscribe__action"><a class="ds-button ds-button--secondary" href="%1$s" target="_blank" rel="noopener">%2$s'
		. '<span class="screen-reader-text">%3$s</span></a></div>',
		esc_url( $url ),
		esc_html__( 'Подписаться', 'designstack-core' ),
		esc_html__( 'откроется в новой вкладке', 'designstack-core' )
	);

	if ( 'footer' === $variant ) {
		return sprintf( '<div class="ds-subscribe ds-subscribe--footer">%s</div>', $button );
	}

	return sprintf(
		'<div class="ds-subscribe"><div class="ds-subscribe__text">'
		. '<h2 class="ds-section__title">%1$s</h2><p>%2$s</p></div>%3$s</div>',
		esc_html__( 'Дайджест раз в неделю', 'designstack-core' ),
		esc_html__( 'Новые ресурсы и то, что изменилось у старых, — одним постом в Telegram вместо двадцати каналов.', 'designstack-core' ),
		$button
	);
}

/**
 * Заголовки секций с карточками записей.
 *
 * Слова из docs/VOICE.md: «Свежие подборки», «Другие подборки», «Все подборки», «Все выпуски».
 *
 * @param string $category Слаг категории.
 * @param string $variant  fresh | other.
 * @return array{0: string, 1: string} Заголовок секции и подпись ссылки «все».
 */
function designstack_core_post_section_words( string $category, string $variant ): array {
	$words = array(
		'collections' => array(
			'fresh' => __( 'Свежие подборки', 'designstack-core' ),
			'other' => __( 'Другие подборки', 'designstack-core' ),
			'more'  => __( 'Все подборки', 'designstack-core' ),
		),
		'digest'      => array(
			'fresh' => __( 'Дайджест', 'designstack-core' ),
			'other' => __( 'Другие выпуски', 'designstack-core' ),
			'more'  => __( 'Все выпуски', 'designstack-core' ),
		),
		'reviews'     => array(
			'fresh' => __( 'Обзоры', 'designstack-core' ),
			'other' => __( 'Другие обзоры', 'designstack-core' ),
			'more'  => __( 'Все обзоры', 'designstack-core' ),
		),
	);

	if ( ! isset( $words[ $category ] ) ) {
		return array( '', '' );
	}

	$key = 'other' === $variant ? 'other' : 'fresh';

	return array( $words[ $category ][ $key ], $words[ $category ]['more'] );
}

/**
 * Секция карточек записей: подборки, выпуски или обзоры.
 *
 * @param string $category Слаг категории.
 * @param string $variant  fresh | other.
 * @return string
 */
function designstack_core_render_post_section( string $category, string $variant = 'fresh' ): string {
	if ( 'auto' === $category ) {
		$category = is_singular( 'post' ) ? designstack_core_entry_category( (int) get_queried_object_id() ) : '';

		// У выпуска вместо «Других выпусков» стоит навигация по соседям (решение c4).
		if ( 'digest' === $category ) {
			return '';
		}
	}

	list( $title, $label ) = designstack_core_post_section_words( $category, $variant );

	if ( '' === $title ) {
		return '';
	}

	// «Другие подборки» не показывают текущую запись.
	$exclude = 'other' === $variant && is_singular( 'post' ) ? (int) get_queried_object_id() : 0;

	return designstack_core_render_post_list( $category, $title, $label, $exclude );
}

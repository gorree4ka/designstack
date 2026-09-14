<?php
/**
 * Разметка страниц каталога: шапка архива, фильтры, чипсы, пагинация, шапка ресурса, оценка, аналоги.
 *
 * Классы повторяют каталог паттернов (`docs/ds/components.md`, раздел «Контракт разметки»):
 * нового класса здесь не появляется — сначала строка в каталоге, потом код.
 * Выборку по параметрам эти функции не делают: фильтры и поиск включает этап 14.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Шапка архива: заголовок раздела или темы и число выдачи.
 *
 * @return string
 */
function designstack_core_render_archive_header(): string {
	global $wp_query;

	$title = designstack_core_archive_title();

	if ( '' === $title ) {
		return '';
	}

	return sprintf(
		'<div class="ds-page-header"><h1 class="ds-page-header__title">%1$s</h1><p class="ds-meta">%2$s</p></div>',
		esc_html( $title ),
		esc_html( designstack_core_archive_count_line( (int) $wp_query->found_posts ) )
	);
}

/**
 * Группы фильтров раздела: набор осей зависит от типа (`docs/ia/wireframes/tools.md`).
 *
 * Значения каждой оси берутся из `designstack_core_filter_options()` — там же, где их проверяет
 * выборка. Два списка разошлись бы при первой правке: панель показывала бы значение, по которому
 * ничего не находится.
 *
 * @param string $type Слаг типа ресурса.
 * @return array<int, array{legend: string, name: string, options: array<string, string>}>
 */
/**
 * Оси-флажки: значение одно по своей природе, снятый флажок значит «неважно».
 *
 * @return array<int, string>
 */
function designstack_core_toggle_axes(): array {
	return array( 'is_jobs' );
}

function designstack_core_filter_groups( string $type ): array {
	$group = static function ( string $legend, string $name ): array {
		return array(
			'legend'  => $legend,
			'name'    => $name,
			'options' => designstack_core_filter_options( $name ),
		);
	};

	$axes = array(
		'learning'  => array(
			array( __( 'Формат', 'designstack-core' ), 'format' ),
			array( __( 'Грейд', 'designstack-core' ), 'level' ),
			array( __( 'Язык', 'designstack-core' ), 'language' ),
			array( __( 'Цена', 'designstack-core' ), 'pricing' ),
			array( __( 'Доступ из РФ', 'designstack-core' ), 'ru_open' ),
		),
		'asset'     => array(
			array( __( 'Лицензия', 'designstack-core' ), 'license' ),
			array( __( 'Формат файла', 'designstack-core' ), 'file_format' ),
			array( __( 'Кириллица', 'designstack-core' ), 'cyrillic' ),
			array( __( 'Доступ из РФ', 'designstack-core' ), 'ru_open' ),
		),
		'community' => array(
			array( __( 'Платформа', 'designstack-core' ), 'platform' ),
			array( __( 'Есть вакансии', 'designstack-core' ), 'is_jobs' ),
			array( __( 'Доступ из РФ', 'designstack-core' ), 'ru_open' ),
		),
		'tool'      => array(
			array( __( 'Тема', 'designstack-core' ), 'topic' ),
			array( __( 'Цена', 'designstack-core' ), 'pricing' ),
			array( __( 'Доступ из РФ', 'designstack-core' ), 'ru_open' ),
			array( __( 'Оплата из РФ', 'designstack-core' ), 'ru_payment' ),
			array( __( 'Платформа', 'designstack-core' ), 'platforms' ),
			array( __( 'Грейд', 'designstack-core' ), 'level' ),
		),
	);

	$groups = array();

	foreach ( $axes[ $type ] ?? $axes['tool'] as $axis ) {
		$groups[] = $group( $axis[0], $axis[1] );
	}

	return $groups;
}

/**
 * Панель фильтров раздела.
 *
 * Без JavaScript панель — обычная форма GET: отмечаем значения, жмём «Применить», адрес
 * собирает браузер. Длинный вид `pricing[]=…` понимается наравне с коротким `pricing=a,b`.
 *
 * @param string $variant sidebar | sheet.
 * @return string
 */
function designstack_core_render_filters( string $variant = 'sidebar' ): string {
	// Выдача пуста — фильтровать нечего только тогда, когда и фильтров нет:
	// иначе панель нужна, чтобы снять лишнее (US-19).
	global $wp_query;

	$active = designstack_core_active_filters();

	if ( ! (int) $wp_query->found_posts && ! $active ) {
		return '';
	}

	$term = designstack_core_archive_term();

	if ( ! $term || 'resource_type' !== $term->taxonomy ) {
		return '';
	}

	$action = (string) get_term_link( $term );
	$out    = '';

	$available = designstack_core_available_values( $term->slug );

	foreach ( designstack_core_filter_groups( $term->slug ) as $group ) {
		// Значение, под которое нет ни одного ресурса раздела, в панель не попадает (US-14).
		if ( isset( $available[ $group['name'] ] ) ) {
			$group['options'] = array_intersect_key(
				$group['options'],
				array_flip( $available[ $group['name'] ] )
			);
		}

		// Группа с одним вариантом фильтром не является: выбор, который ничего не отсеивает,
		// занимает место и обещает работу, которой не делает (продолжение US-14).
		// Исключение — флажки вроде «Есть вакансии»: у них значение одно по своей природе,
		// и снятый флажок означает «неважно», а не отсутствие выбора.
		$toggle = in_array( $group['name'], designstack_core_toggle_axes(), true );

		if ( ! $group['options'] || ( ! $toggle && count( $group['options'] ) < 2 ) ) {
			continue;
		}

		$chosen  = $active[ $group['name'] ] ?? array();
		$options = '';

		foreach ( $group['options'] as $value => $label ) {
			$options .= sprintf(
				'<label class="ds-filters__option"><input type="checkbox" name="%1$s[]" value="%2$s"%3$s>%4$s</label>',
				esc_attr( $group['name'] ),
				esc_attr( (string) $value ),
				in_array( (string) $value, $chosen, true ) ? ' checked' : '',
				esc_html( $label )
			);
		}

		$out .= sprintf(
			'<fieldset class="ds-filters__group"><legend class="ds-filters__legend">%1$s</legend>%2$s</fieldset>',
			esc_html( $group['legend'] ),
			$options
		);
	}

	if ( '' === $out ) {
		return '';
	}

	$sort   = designstack_core_current_sort();
	$hidden = 'checked' !== $sort
		? sprintf( '<input type="hidden" name="sort" value="%s">', esc_attr( $sort ) )
		: '';

	$reset = $active
		? sprintf(
			'<a class="ds-link ds-chips__reset" href="%1$s">%2$s</a>',
			esc_url( designstack_core_filter_url( array(), $sort ) ),
			esc_html__( 'Сбросить фильтры', 'designstack-core' )
		)
		: '';

	// Шапка с закрытием нужна на узком экране, где панель выезжает снизу; шире 900 её прячет CSS.
	$head = sprintf(
		'<div class="ds-filters__head"><p class="ds-filters__title">%1$s</p>'
		. '<a class="ds-button ds-button--icon ds-filters__close" href="#ds-main" data-ds-filters-close>%2$s'
		. '<span class="screen-reader-text">%3$s</span></a></div>',
		esc_html__( 'Фильтры', 'designstack-core' ),
		designstack_core_icon( 'x' ),
		esc_html__( 'Закрыть', 'designstack-core' )
	);

	$actions = sprintf(
		'<div class="ds-filters__actions"><button type="submit" class="ds-button ds-button--primary">%1$s</button>%2$s</div>',
		esc_html__( 'Применить', 'designstack-core' ),
		$reset
	);

	return sprintf(
		'<form class="ds-filters ds-filters--%1$s" id="ds-filters" method="get" action="%2$s" aria-label="%3$s"'
		. ' data-track="filter_apply">%4$s%5$s%6$s%7$s</form>',
		esc_attr( 'sheet' === $variant ? 'sheet' : 'sidebar' ),
		esc_url( $action ),
		esc_attr__( 'Фильтры', 'designstack-core' ),
		$head,
		$out,
		$hidden,
		$actions
	);
}

/**
 * Подпись значения фильтра для чипса.
 *
 * @param string $key   Ось фильтра.
 * @param string $value Значение.
 * @return string
 */
function designstack_core_filter_label( string $key, string $value ): string {
	if ( 'resource_type' === $key ) {
		return designstack_core_section_name( $value );
	}

	$options = designstack_core_filter_options( $key );

	return (string) ( $options[ $value ] ?? $value );
}

/**
 * Ряд чипсов: активные фильтры в разделе, выбор типа на странице темы.
 *
 * @param string $variant choice | removable.
 * @return string
 */
function designstack_core_render_chips( string $variant = 'choice' ): string {
	global $wp_query;

	$term = designstack_core_archive_term();

	if ( ! $term ) {
		return '';
	}

	$active = designstack_core_active_filters();
	$sort   = designstack_core_current_sort();

	if ( 'removable' === $variant ) {
		if ( ! (int) $wp_query->found_posts && ! $active ) {
			return '';
		}

		$count = 0;

		foreach ( $active as $values ) {
			$count += count( $values );
		}

		// Без JavaScript панель раскрывает сам адрес (#ds-filters), с ним — скрипт с ловушкой фокуса.
		$chips = sprintf(
			'<a class="ds-button ds-button--secondary ds-button--sm ds-chips__toggle" href="#ds-filters" '
			. 'aria-expanded="false" aria-controls="ds-filters" data-ds-filters-open>%s</a>',
			$count
				/* translators: %d — число активных фильтров. */
				? esc_html( sprintf( __( 'Фильтры (%d)', 'designstack-core' ), $count ) )
				: esc_html__( 'Фильтры', 'designstack-core' )
		);

		foreach ( $active as $key => $values ) {
			foreach ( $values as $value ) {
				$rest = $active;
				$left = array_values( array_diff( $values, array( $value ) ) );

				if ( $left ) {
					$rest[ $key ] = $left;
				} else {
					unset( $rest[ $key ] );
				}

				$label  = designstack_core_filter_label( $key, $value );
				$chips .= sprintf(
					'<a class="ds-chip" href="%1$s"><span class="ds-chip__label">%2$s</span>%3$s'
					/* translators: %s — значение фильтра. */
					. '<span class="screen-reader-text">%4$s</span></a>',
					esc_url( designstack_core_filter_url( $rest, $sort ) ),
					esc_html( $label ),
					designstack_core_icon( 'x' ),
					esc_html( sprintf( __( 'Снять фильтр: %s', 'designstack-core' ), $label ) )
				);
			}
		}

		if ( $active ) {
			$chips .= sprintf(
				'<a class="ds-link ds-chips__reset" href="%1$s">%2$s</a>',
				esc_url( designstack_core_filter_url( array(), $sort ) ),
				esc_html__( 'Сбросить фильтры', 'designstack-core' )
			);
		}

		return sprintf( '<div class="ds-chips ds-chips--removable">%s</div>', $chips );
	}

	if ( ! (int) $wp_query->found_posts && ! $active ) {
		return '';
	}

	$current = $active['resource_type'] ?? array();
	$rest    = $active;
	unset( $rest['resource_type'] );

	$chips = $current
		? sprintf(
			'<a class="ds-chip" href="%1$s">%2$s</a>',
			esc_url( designstack_core_filter_url( $rest, $sort ) ),
			esc_html__( 'Все', 'designstack-core' )
		)
		: sprintf( '<span class="ds-chip" aria-current="page">%s</span>', esc_html__( 'Все', 'designstack-core' ) );

	foreach ( designstack_core_type_sections() as $slug => $section ) {
		if ( in_array( $slug, $current, true ) ) {
			$chips .= sprintf( '<span class="ds-chip" aria-current="page">%s</span>', esc_html( $section['name'] ) );
			continue;
		}

		$chips .= sprintf(
			'<a class="ds-chip" href="%1$s">%2$s</a>',
			esc_url( designstack_core_filter_url( array_merge( $rest, array( 'resource_type' => array( $slug ) ) ), $sort ) ),
			esc_html( $section['name'] )
		);
	}

	return sprintf(
		'<nav class="ds-chips ds-chips--choice" aria-label="%1$s">%2$s</nav>',
		esc_attr__( 'Тип ресурса', 'designstack-core' ),
		$chips
	);
}

/**
 * Переключатель порядка выдачи.
 *
 * @return string
 */
function designstack_core_render_sort(): string {
	global $wp_query;

	if ( ! designstack_core_archive_term() || (int) $wp_query->found_posts < 2 ) {
		return '';
	}

	$current = designstack_core_current_sort();
	$active  = designstack_core_active_filters();
	$options = '';

	foreach ( designstack_core_sort_options() as $slug => $label ) {
		$options .= $slug === $current
			? sprintf( '<span class="ds-chip" aria-current="true">%s</span>', esc_html( $label ) )
			: sprintf(
				'<a class="ds-chip" href="%1$s">%2$s</a>',
				esc_url( designstack_core_filter_url( $active, $slug ) ),
				esc_html( $label )
			);
	}

	return sprintf(
		'<nav class="ds-sort" aria-label="%1$s"><span class="ds-sort__label">%2$s</span>%3$s</nav>',
		esc_attr__( 'Порядок выдачи', 'designstack-core' ),
		esc_html__( 'Сортировка', 'designstack-core' ),
		$options
	);
}

/**
 * Пагинация основного запроса. Одна страница — блока нет (решение t6).
 *
 * @return string
 */
function designstack_core_render_pagination(): string {
	global $wp_query;

	$total = (int) $wp_query->max_num_pages;

	if ( $total < 2 ) {
		return '';
	}

	$current = max( 1, (int) get_query_var( 'paged' ) );

	$prev = $current > 1
		? sprintf(
			'<a class="ds-button ds-button--secondary ds-button--sm" href="%1$s">%2$s%3$s</a>',
			esc_url( (string) get_pagenum_link( $current - 1 ) ),
			designstack_core_icon( 'chevron-left' ),
			esc_html__( 'Назад', 'designstack-core' )
		)
		: sprintf(
			'<span class="ds-button ds-button--secondary ds-button--sm is-disabled">%1$s%2$s</span>',
			designstack_core_icon( 'chevron-left' ),
			esc_html__( 'Назад', 'designstack-core' )
		);

	$next = $current < $total
		? sprintf(
			'<a class="ds-button ds-button--secondary ds-button--sm" href="%1$s">%2$s%3$s</a>',
			esc_url( (string) get_pagenum_link( $current + 1 ) ),
			esc_html__( 'Вперёд', 'designstack-core' ),
			designstack_core_icon( 'chevron-right' )
		)
		: sprintf(
			'<span class="ds-button ds-button--secondary ds-button--sm is-disabled">%1$s%2$s</span>',
			esc_html__( 'Вперёд', 'designstack-core' ),
			designstack_core_icon( 'chevron-right' )
		);

	$numbers = '';

	for ( $page = 1; $page <= $total; $page++ ) {
		$numbers .= $page === $current
			? sprintf( '<span class="ds-pagination__page" aria-current="page">%d</span>', $page )
			: sprintf(
				'<a class="ds-pagination__page" href="%1$s">%2$d</a>',
				esc_url( (string) get_pagenum_link( $page ) ),
				$page
			);
	}

	return sprintf(
		'<nav class="ds-pagination" aria-label="%1$s">%2$s<span class="ds-pagination__numbers">%3$s</span>'
		. '<span class="ds-pagination__summary ds-meta">%4$s</span>%5$s</nav>',
		esc_attr__( 'Страницы', 'designstack-core' ),
		$prev,
		$numbers,
		esc_html( sprintf( __( 'Страница %1$d из %2$d', 'designstack-core' ), $current, $total ) ),
		$next
	);
}

/**
 * Первый экран страницы ресурса.
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_render_hero( int $post_id ): string {
	$title   = get_the_title( $post_id );
	$type    = designstack_core_get_type( $post_id );
	$term    = $type ? get_term_by( 'slug', $type, 'resource_type' ) : null;
	$verdict = (string) designstack_core_get_field( $post_id, 'verdict' );
	$url     = (string) designstack_core_get_field( $post_id, 'url' );
	$status  = (string) designstack_core_get_field( $post_id, 'status' );
	$analogs = (array) designstack_core_get_field( $post_id, 'ru_alternative' );
	$checked = designstack_core_checked_line( $post_id );

	$out = '<div class="ds-hero"><div class="ds-hero__head">';
	$out .= sprintf(
		'<span class="ds-logo ds-logo--lg" aria-hidden="true">%s</span>',
		esc_html( mb_substr( $title, 0, 1 ) )
	);
	$out .= '<div class="ds-hero__titles">';
	$out .= sprintf( '<h1 class="ds-hero__title">%s</h1>', esc_html( $title ) );

	if ( $term instanceof WP_Term ) {
		$out .= sprintf( '<span class="ds-hero__type">%s</span>', esc_html( $term->name ) );
	}

	$out .= '</div></div>';

	if ( $verdict ) {
		$out .= sprintf( '<p class="ds-hero__verdict">%s</p>', esc_html( $verdict ) );
	}

	$out .= designstack_core_badges( $post_id );

	// Плашка состояния стоит выше кнопки перехода: закрытый ресурс читается до попытки уйти (D31).
	if ( 'dead' === $status ) {
		$out .= designstack_core_render_notice(
			'dead',
			'circle-x',
			__( 'Закрыт', 'designstack-core' ),
			__( 'Ресурс больше не работает. Запись оставляем ради истории и ссылки на аналог.', 'designstack-core' ),
			$analogs
				? sprintf(
					'<a class="ds-button ds-button--primary" href="#analogs" data-track="ru_alternative_click" data-track-resource-type="%1$s">%2$s</a>',
					esc_attr( (string) designstack_core_get_type( $post_id ) ),
					esc_html__( 'Показать аналог', 'designstack-core' )
				)
				// Аналога нет — тупик: говорим об этом прямо и даём следующий шаг.
				: sprintf(
					'<span class="ds-notice__note">%1$s</span><a class="ds-link" href="%2$s">%3$s</a>',
					esc_html__( 'Аналог пока не подобрали.', 'designstack-core' ),
					esc_url( home_url( '/suggest/' ) ),
					esc_html__( 'Предложить ресурс', 'designstack-core' )
				)
		);
	} elseif ( 'changed' === $status ) {
		$out .= designstack_core_render_notice(
			'changed',
			'triangle-alert',
			__( 'Условия изменились', 'designstack-core' ),
			__( 'С прошлой проверки поменялись цена, тариф или доступ. Что именно — в оценке куратора.', 'designstack-core' )
		);
	} elseif ( designstack_core_is_stale( $post_id ) ) {
		$out .= designstack_core_render_notice(
			'stale',
			'clock',
			__( 'Давно не проверяли', 'designstack-core' ),
			__( 'Проверено больше 90 дней назад, куратор перепроверит. Условия могли измениться.', 'designstack-core' )
		);
	}

	$actions = '';

	// У закрытого ресурса кнопки перехода нет (D31).
	if ( 'dead' !== $status && $url ) {
		$actions .= sprintf(
			'<a class="ds-button ds-button--primary ds-button--lg" href="%1$s" target="_blank" rel="noopener"'
			. ' data-track="resource_outbound" %4$s>%2$s<span class="screen-reader-text">%3$s</span></a>',
			esc_url( $url ),
			esc_html__( 'Перейти на сайт', 'designstack-core' ),
			esc_html__( 'откроется в новой вкладке', 'designstack-core' ),
			designstack_core_track_attrs( get_the_ID() )
		);
	}

	if ( $checked ) {
		$actions .= sprintf( '<p class="ds-meta ds-meta--xs">%s</p>', esc_html( $checked ) );
	}

	if ( $actions ) {
		$out .= sprintf( '<div class="ds-hero__actions">%s</div>', $actions );
	}

	return $out . '</div>';
}

/**
 * Оценка куратора тремя частями (D67).
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_render_review( int $post_id ): string {
	$parts = array(
		array( __( 'Кому подходит', 'designstack-core' ), designstack_core_get_field( $post_id, 'review_for' ) ),
		array( __( 'За что', 'designstack-core' ), designstack_core_get_field( $post_id, 'review_why' ) ),
		array( __( 'Когда не подойдёт', 'designstack-core' ), designstack_core_get_field( $post_id, 'review_not' ) ),
	);

	$body = '';

	foreach ( $parts as $part ) {
		$text = (string) $part[1];

		if ( '' === $text ) {
			continue;
		}

		$body .= sprintf(
			'<div class="ds-review__part"><p class="ds-review__label">%1$s</p><p class="ds-review__text">%2$s</p></div>',
			esc_html( $part[0] ),
			esc_html( $text )
		);
	}

	if ( '' === $body ) {
		return '';
	}

	// Имени куратора на странице нет, пока оно не выбрано (O2): подпись без имени, решение r5.
	$sign = sprintf(
		'<a class="ds-link ds-review__sign" href="%1$s"><span class="ds-logo ds-logo--rimmed" aria-hidden="true">D</span>%2$s</a>',
		esc_url( home_url( '/about/#curator' ) ),
		esc_html__( 'Куратор DesignStack', 'designstack-core' )
	);

	return sprintf(
		'<section class="ds-review" aria-labelledby="ds-review-title">'
		. '<h2 class="ds-section__title" id="ds-review-title">%1$s</h2>%2$s%3$s</section>',
		esc_html__( 'Оценка куратора', 'designstack-core' ),
		$body,
		$sign
	);
}

/**
 * Блок аналогов: карточки из поля `ru_alternative`.
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_render_analogs( int $post_id ): string {
	$cards   = '';
	$analogs = array_filter( array_map( 'absint', (array) designstack_core_get_field( $post_id, 'ru_alternative' ) ) );

	if ( $analogs ) {
		// Карточки аналогов читают поля и темы: греем кеш одним запросом, а не по записи.
		_prime_post_caches( $analogs, true, true );
	}

	foreach ( $analogs as $analog ) {
		$analog = absint( $analog );

		if ( ! $analog || 'resource' !== get_post_type( $analog ) || 'publish' !== get_post_status( $analog ) ) {
			continue;
		}

		$cards .= designstack_core_render_card( $analog );
	}

	if ( '' === $cards ) {
		return '';
	}

	return sprintf(
		'<section class="ds-section" id="analogs"><div class="ds-section__head">'
		. '<h2 class="ds-section__title">%1$s</h2></div>'
		. '<div class="ds-section__body"><div class="ds-resource-list ds-resource-list--grid">%2$s</div></div></section>',
		esc_html__( 'Аналог из России', 'designstack-core' ),
		$cards
	);
}

/**
 * Пустая выдача архива: почему пусто и что делать дальше (US-19).
 *
 * @return string
 */
function designstack_core_render_empty_archive(): string {
	$term   = designstack_core_archive_term();
	$active = designstack_core_active_filters();
	$sort   = designstack_core_current_sort();
	$link   = sprintf(
		'<a class="ds-link" href="%1$s">%2$s</a>',
		esc_url( home_url( '/suggest/' ) ),
		esc_html__( 'Предложить ресурс', 'designstack-core' )
	);

	// Фильтров нет — пусто само по себе: раздел или тема ещё не наполнены.
	if ( ! $active ) {
		$title = $term && 'topic' === $term->taxonomy
			? __( 'В этой теме пока нет ресурсов', 'designstack-core' )
			: __( 'В разделе пока нет ресурсов', 'designstack-core' );

		return designstack_core_render_empty( 'section', $title, '', $link );
	}

	$names = array();

	foreach ( $active as $key => $values ) {
		foreach ( $values as $value ) {
			$names[] = '«' . designstack_core_filter_label( $key, $value ) . '»';
		}
	}

	$actions = sprintf(
		'<a class="ds-button ds-button--primary" href="%1$s">%2$s</a>%3$s',
		esc_url( designstack_core_filter_url( array(), $sort ) ),
		esc_html__( 'Сбросить фильтры', 'designstack-core' ),
		$link
	);

	$out = designstack_core_render_empty(
		'filters',
		__( 'По таким условиям ничего нет', 'designstack-core' ),
		sprintf(
			/* translators: %s — перечень активных фильтров в кавычках. */
			__( 'Выбрано: %s. Попробуй снять один из фильтров.', 'designstack-core' ),
			implode( ', ', $names )
		),
		$actions
	);

	// Если среди фильтров есть тема, показываем её ресурсы без остальных условий (US-19).
	$topic = $active['topic'][0] ?? ( $term && 'topic' === $term->taxonomy ? $term->slug : '' );

	if ( ! $topic ) {
		return $out;
	}

	$term_object = get_term_by( 'slug', $topic, 'topic' );

	if ( ! $term_object instanceof WP_Term ) {
		return $out;
	}

	$posts = get_posts(
		array(
			'post_type'      => 'resource',
			'post_status'    => 'publish',
			'posts_per_page' => 6,
			'no_found_rows'  => true,
			'meta_key'       => 'checked_at',
			'orderby'        => 'meta_value',
			'order'          => 'DESC',
			'tax_query'      => array(
				array(
					'taxonomy' => 'topic',
					'field'    => 'slug',
					'terms'    => $topic,
				),
			),
		)
	);

	if ( ! $posts ) {
		return $out;
	}

	$cards = '';

	foreach ( $posts as $post ) {
		$cards .= designstack_core_render_card( (int) $post->ID );
	}

	return $out . designstack_core_section(
		sprintf(
			/* translators: %s — название темы. */
			__( '%s без других фильтров', 'designstack-core' ),
			$term_object->name
		),
		'',
		sprintf( '<div class="ds-resource-list ds-resource-list--grid">%s</div>', $cards )
	);
}

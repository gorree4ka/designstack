<?php
/**
 * Служебные страницы: выдача поиска и «Такой страницы нет».
 *
 * Поиск здесь — встроенный поиск WordPress по каталогу и записям. Своей выборки по параметрам
 * этот файл не делает: ранжирование и фильтры выдачи включает этап 14.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Строка выдачи поиска: «3 результата».
 *
 * @param int $number Число найденного.
 * @return string
 */
function designstack_core_results_line( int $number ): string {
	return sprintf(
		'%1$d %2$s',
		$number,
		designstack_core_plural(
			$number,
			array(
				__( 'результат', 'designstack-core' ),
				__( 'результата', 'designstack-core' ),
				__( 'результатов', 'designstack-core' ),
			)
		)
	);
}

/**
 * Страница поиска: заголовок, поле с запросом, число найденного и карточки.
 *
 * @return string
 */
function designstack_core_render_search_results(): string {
	global $wp_query;

	$query = get_search_query();
	$found = (int) $wp_query->found_posts;

	$head = sprintf( '<h1 class="ds-page-header__title">%s</h1>', esc_html__( 'Поиск', 'designstack-core' ) );
	$head .= designstack_core_render_search( 'results' );

	if ( '' !== $query && $found ) {
		$head .= sprintf( '<p class="ds-meta">%s</p>', esc_html( designstack_core_results_line( $found ) ) );
	}

	$out = sprintf( '<div class="ds-page-header">%s</div>', $head );

	if ( '' === $query ) {
		return $out;
	}

	$cards = '';

	// Ресурсы и записи идут одной сеткой, в порядке, который вернул поиск ядра (решение s4).
	foreach ( (array) $wp_query->posts as $post ) {
		if ( ! $post instanceof WP_Post ) {
			continue;
		}

		if ( 'resource' === $post->post_type ) {
			$cards .= designstack_core_render_card( (int) $post->ID, 2 );
		} else {
			// Записи и страницы — карточкой записи: иначе число найденного не сходится с показанным.
			$cards .= designstack_core_render_post_card( (int) $post->ID, true, 2 );
		}
	}

	if ( '' === $cards ) {
		// Длинный запрос в заголовок целиком не ставим: он там не читается, а в поле остаётся весь.
		$shown = mb_strlen( $query ) > 60 ? mb_substr( $query, 0, 60 ) . '…' : $query;

		// Пустой поиск — это состояние страницы, а не клик: маркер читает track.js
		// при загрузке. По длине запроса видно, ищут словом или фразой.
		$out .= sprintf(
			'<span hidden data-track-on-load="search_empty" data-track-query-length="%d"></span>',
			mb_strlen( $query )
		);

		return $out . designstack_core_render_empty(
			'search',
			sprintf(
				/* translators: %s — поисковый запрос. */
				__( 'По запросу «%s» ничего нет', 'designstack-core' ),
				$shown
			),
			__( 'Попробуй короче или другими словами. Если ресурса нет в каталоге — предложи его.', 'designstack-core' ),
			sprintf(
				'<a class="ds-link" href="%1$s">%2$s</a>',
				esc_url( home_url( '/suggest/' ) ),
				esc_html__( 'Предложить ресурс', 'designstack-core' )
			)
		);
	}

	return $out . sprintf( '<div class="ds-resource-list ds-resource-list--grid">%s</div>', $cards );
}

/**
 * Страница 404: причина словами и что делать дальше.
 *
 * @return string
 */
function designstack_core_render_not_found(): string {
	return designstack_core_render_empty(
		'not-found',
		__( 'Такой страницы нет', 'designstack-core' ),
		__( 'Адрес мог измениться или в нём опечатка. Найди ресурс поиском или открой раздел.', 'designstack-core' ),
		'',
		'h1'
	);
}

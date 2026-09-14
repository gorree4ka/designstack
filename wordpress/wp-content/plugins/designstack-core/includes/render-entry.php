<?php
/**
 * Разметка редакции: шапка записи, навигация по выпускам, архив записей.
 *
 * Один шаблон обслуживает подборку, выпуск и обзор — раскладку различают сами блоки
 * по категории записи (`docs/ds/screens/collection.md`, `digest-issue.md`).
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Слаг раздела редакции у записи.
 *
 * @param int $post_id Идентификатор записи.
 * @return string collections | digest | reviews | ''.
 */
function designstack_core_entry_category( int $post_id ): string {
	foreach ( (array) get_the_category( $post_id ) as $term ) {
		if ( in_array( $term->slug, array( 'collections', 'digest', 'reviews' ), true ) ) {
			return $term->slug;
		}
	}

	return '';
}

/**
 * Формы счёта записей по разделу.
 *
 * @param string $category Слаг категории.
 * @return array{0: string, 1: string, 2: string}
 */
function designstack_core_entry_forms( string $category ): array {
	$forms = array(
		'collections' => array(
			__( 'подборка', 'designstack-core' ),
			__( 'подборки', 'designstack-core' ),
			__( 'подборок', 'designstack-core' ),
		),
		'digest'      => array(
			__( 'выпуск', 'designstack-core' ),
			__( 'выпуска', 'designstack-core' ),
			__( 'выпусков', 'designstack-core' ),
		),
		'reviews'     => array(
			__( 'обзор', 'designstack-core' ),
			__( 'обзора', 'designstack-core' ),
			__( 'обзоров', 'designstack-core' ),
		),
	);

	return $forms[ $category ] ?? array(
		__( 'запись', 'designstack-core' ),
		__( 'записи', 'designstack-core' ),
		__( 'записей', 'designstack-core' ),
	);
}

/**
 * Шапка записи: заголовок, описание и мета.
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_render_entry_header( int $post_id ): string {
	$title = get_the_title( $post_id );

	if ( '' === $title ) {
		return '';
	}

	$out = sprintf( '<h1 class="ds-page-header__title">%s</h1>', esc_html( $title ) );

	$lead = get_the_excerpt( $post_id );

	if ( $lead ) {
		$out .= sprintf( '<p class="ds-page-header__lead">%s</p>', esc_html( $lead ) );
	}

	$meta  = array();
	$count = designstack_core_count_resources( $post_id );

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

	// Находки считаются, как только куратор вставит их в запись.
	$finds = designstack_core_count_finds( $post_id );

	if ( $finds ) {
		$meta[] = sprintf(
			'%1$d %2$s',
			$finds,
			designstack_core_plural(
				$finds,
				array(
					__( 'находка', 'designstack-core' ),
					__( 'находки', 'designstack-core' ),
					__( 'находок', 'designstack-core' ),
				)
			)
		);
	}

	$time   = (int) get_post_time( 'U', false, $post_id );
	$meta[] = date_i18n( 'j', $time ) . "\u{00A0}" . mb_strtolower( date_i18n( 'M', $time ) ) . ' ' . date_i18n( 'Y', $time );

	$out .= sprintf( '<p class="ds-meta">%s</p>', esc_html( designstack_core_join( $meta ) ) );

	return sprintf( '<div class="ds-page-header">%s</div>', $out );
}

/**
 * Сколько находок недели стоит в записи.
 *
 * @param int $post_id Идентификатор записи.
 * @return int
 */
function designstack_core_count_finds( int $post_id ): int {
	$post = get_post( $post_id );

	if ( ! $post ) {
		return 0;
	}

	return substr_count( (string) $post->post_content, 'designstack/issue-find' );
}

/**
 * Навигация по выпускам: соседние выпуски и «Все выпуски».
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_render_issue_nav( int $post_id ): string {
	if ( 'digest' !== designstack_core_entry_category( $post_id ) ) {
		return '';
	}

	$term = get_category_by_slug( 'digest' );

	if ( ! $term ) {
		return '';
	}

	$neighbour = static function ( int $post_id, string $direction ) use ( $term ): string {
		$post = get_post( $post_id );

		if ( ! $post ) {
			return '';
		}

		$found = get_posts(
			array(
				'post_type'      => 'post',
				'post_status'    => 'publish',
				'posts_per_page' => 1,
				'no_found_rows'  => true,
				'cat'            => $term->term_id,
				'exclude'        => array( $post_id ),
				'order'          => 'prev' === $direction ? 'DESC' : 'ASC',
				'orderby'        => 'date',
				'date_query'     => array(
					array(
						'prev' === $direction ? 'before' : 'after' => $post->post_date,
						'inclusive' => false,
					),
				),
			)
		);

		if ( ! $found ) {
			return '';
		}

		$label = 'prev' === $direction
			? __( 'Предыдущий выпуск', 'designstack-core' )
			: __( 'Следующий выпуск', 'designstack-core' );

		return sprintf(
			'<a class="ds-link ds-issue-nav__%1$s" href="%2$s">%3$s%4$s%5$s<span class="ds-meta">%6$s</span></a>',
			esc_attr( $direction ),
			esc_url( (string) get_permalink( $found[0] ) ),
			'prev' === $direction ? designstack_core_icon( 'chevron-left' ) : '',
			esc_html( $label ),
			'next' === $direction ? designstack_core_icon( 'chevron-right' ) : '',
			esc_html( get_the_title( $found[0] ) )
		);
	};

	$all = sprintf(
		'<a class="ds-link ds-link--standalone ds-issue-nav__all" href="%1$s">%2$s</a>',
		esc_url( (string) get_category_link( $term ) ),
		esc_html__( 'Все выпуски', 'designstack-core' )
	);

	return sprintf(
		'<nav class="ds-issue-nav" aria-label="%1$s">%2$s%3$s%4$s</nav>',
		esc_attr__( 'Выпуски дайджеста', 'designstack-core' ),
		$neighbour( $post_id, 'prev' ),
		$all,
		$neighbour( $post_id, 'next' )
	);
}

/**
 * Архив редакции: карточки записей основного запроса.
 *
 * @return string
 */
function designstack_core_render_post_archive(): string {
	global $wp_query;

	$cards = '';

	foreach ( (array) $wp_query->posts as $post ) {
		if ( $post instanceof WP_Post && 'post' === $post->post_type ) {
			$cards .= designstack_core_render_post_card( (int) $post->ID, false, 2 );
		}
	}

	if ( '' === $cards ) {
		$term  = get_queried_object();
		$slug  = $term instanceof WP_Term ? $term->slug : '';
		$empty = array(
			'collections' => __( 'Подборок пока нет', 'designstack-core' ),
			'digest'      => __( 'Выпусков пока нет', 'designstack-core' ),
			'reviews'     => __( 'Обзоров пока нет', 'designstack-core' ),
		);

		return designstack_core_render_empty(
			'section',
			$empty[ $slug ] ?? __( 'Записей пока нет', 'designstack-core' ),
			'',
			sprintf(
				'<a class="ds-link" href="%1$s">%2$s</a>',
				esc_url( home_url( '/collections/' ) ),
				esc_html__( 'Все подборки', 'designstack-core' )
			)
		);
	}

	return sprintf( '<div class="ds-post-list">%s</div>', $cards );
}

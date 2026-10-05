<?php
/**
 * SEO: заголовок, описание, Open Graph, правила индексации, robots.txt.
 *
 * Плагина вроде Yoast в проекте нет намеренно (D119): canonical и закрытие фильтров
 * от индексации написаны на этапе 14 и завязаны на наши query vars, а разметку
 * schema.org всё равно пишем сами — типы записей у нас свои. Остаются заголовок,
 * описание и OG, и они собираются из полей записи, а не заполняются руками.
 *
 * Карта того, что под какой запрос отвечает, — docs/analytics/seo-map.md.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

const DESIGNSTACK_CORE_DESC_MAX = 160;

/**
 * Обрезает текст по границе слова.
 *
 * Поисковик обрежет описание сам, но на середине слова — поэтому режем мы.
 *
 * @param string $text  Текст.
 * @param int    $limit Предел в символах.
 * @return string
 */
function designstack_core_trim( string $text, int $limit = DESIGNSTACK_CORE_DESC_MAX ): string {
	$text = trim( preg_replace( '/\s+/u', ' ', wp_strip_all_tags( $text ) ) );

	if ( mb_strlen( $text ) <= $limit ) {
		return $text;
	}

	$cut = mb_substr( $text, 0, $limit - 1 );
	$at  = mb_strrpos( $cut, ' ' );

	// Хвостовые знаки снимает регулярка с флагом u, а не rtrim: rtrim работает по байтам, и «—» (E2 80 94)
	// в его списке срезал последний байт у «р» (D1 80) и «Д» (D0 94). Строка переставала быть UTF-8,
	// esc_attr() отдавал пустоту, и описание страницы пропадало целиком (вычитка живого сайта 28.09.2026).
	return preg_replace( '/[\s,.;:—-]+$/u', '', false === $at ? $cut : mb_substr( $cut, 0, $at ) ) . '…';
}

/**
 * Описание страницы: собирается из того, что на ней есть.
 *
 * @return string Пустая строка, если описание не нужно (закрытые от индексации страницы).
 */
function designstack_core_description(): string {
	if ( is_search() || is_404() ) {
		return '';
	}

	if ( is_singular( 'resource' ) ) {
		$id   = get_queried_object_id();
		$text = trim(
			designstack_core_get_field( $id, 'review_for' ) . ' ' . designstack_core_get_field( $id, 'review_why' )
		);

		return designstack_core_trim( '' !== $text ? $text : (string) designstack_core_get_field( $id, 'verdict' ) );
	}

	if ( is_singular() || is_page() ) {
		$post = get_queried_object();

		if ( $post instanceof WP_Post ) {
			$text = $post->post_excerpt ? $post->post_excerpt : $post->post_content;

			return designstack_core_trim( $text );
		}
	}

	if ( is_front_page() ) {
		return designstack_core_trim(
			__( 'Инструменты, учёба, ассеты и сообщества для UX/UI-дизайнера. У каждого — цена, доступ из России и дата проверки.', 'designstack-core' )
		);
	}

	if ( is_post_type_archive( 'lesson' ) ) {
		return designstack_core_trim( designstack_core_lessons_lead() );
	}

	$term = designstack_core_archive_term();

	if ( $term ) {
		global $wp_query;

		$count = (int) $wp_query->found_posts;
		$what  = designstack_core_single_filter_label();
		$where = designstack_core_archive_title();

		// «50 ресурсов», а не «50»: число без существительного читается как обрывок.
		$line = designstack_core_count_line( $count );

		if ( '' !== $what ) {
			return designstack_core_trim(
				sprintf(
					/* translators: 1: строка вида «18 ресурсов», 2: раздел, 3: значение фильтра. */
					__( '%1$s в разделе «%2$s»: %3$s. Цена, доступ из России и дата проверки — у каждого.', 'designstack-core' ),
					$line,
					$where,
					$what
				)
			);
		}

		return designstack_core_trim(
			sprintf(
				/* translators: 1: строка вида «50 ресурсов», 2: название раздела или темы. */
				__( '%1$s в разделе «%2$s». У каждого — цена, доступ из России и дата проверки.', 'designstack-core' ),
				$line,
				$where
			)
		);
	}

	return '';
}

/**
 * Подпись единственного активного фильтра — словом из словаря, а не слагом.
 *
 * Нужна там, где страница с одним фильтром работает как самостоятельный ответ
 * на запрос: «Инструменты: бесплатно» ищут, «Инструменты ?pricing=free» — нет.
 *
 * @return string Пусто, если фильтров нет или их больше одного.
 */
function designstack_core_single_filter_label(): string {
	if ( ! function_exists( 'designstack_core_active_filters' ) ) {
		return '';
	}

	$active = designstack_core_active_filters();

	if ( 1 !== count( $active ) ) {
		return '';
	}

	$axis   = (string) array_key_first( $active );
	$values = (array) reset( $active );
	$words  = array();

	// У части осей значение без названия оси не читается: «Ассеты: есть» —
	// бессмыслица, «Ассеты: кириллица есть» — готовый запрос.
	$prefix = array(
		'cyrillic' => __( 'кириллица', 'designstack-core' ),
		'is_jobs'  => __( 'вакансии', 'designstack-core' ),
		'level'    => __( 'для уровня', 'designstack-core' ),
	);

	// Подпись значения берём той же функцией, что рисует чипсы: одно понятие —
	// одно слово и в фильтре, и в заголовке вкладки.
	foreach ( $values as $value ) {
		$label = designstack_core_filter_label( $axis, (string) $value );

		// После двоеточия русское слово идёт со строчной: «Инструменты: бесплатно».
		// Латиницу не трогаем — «Сообщества: telegram» выглядело бы опечаткой.
		if ( preg_match( '/^[А-ЯЁ]/u', $label ) ) {
			$label = mb_strtolower( mb_substr( $label, 0, 1 ) ) . mb_substr( $label, 1 );
		}

		$words[] = $label;
	}

	$out = implode( ', ', array_filter( $words ) );

	return isset( $prefix[ $axis ] ) ? $prefix[ $axis ] . ' ' . $out : $out;
}

/**
 * Печатает описание и Open Graph.
 *
 * Telegram и vc.ru берут превью из OG — это канал дистрибуции из brief §9,
 * а не формальность: без картинки ссылка в канале выглядит как спам.
 *
 * @return void
 */
function designstack_core_head_meta(): void {
	$desc = designstack_core_description();
	$url  = designstack_core_current_url();

	if ( '' !== $desc ) {
		printf( '<meta name="description" content="%s">' . "\n", esc_attr( $desc ) );
		printf( '<meta property="og:description" content="%s">' . "\n", esc_attr( $desc ) );
	}

	printf( '<meta property="og:title" content="%s">' . "\n", esc_attr( designstack_core_og_title() ) );
	printf( '<meta property="og:url" content="%s">' . "\n", esc_url( $url ) );
	printf( '<meta property="og:type" content="%s">' . "\n", is_singular( 'post' ) ? 'article' : 'website' );
	printf( '<meta property="og:site_name" content="%s">' . "\n", esc_attr( get_bloginfo( 'name' ) ) );
	echo '<meta property="og:locale" content="ru_RU">' . "\n";

	$image = designstack_core_og_image();

	if ( '' !== $image ) {
		printf( '<meta property="og:image" content="%s">' . "\n", esc_url( $image ) );
		echo '<meta property="og:image:width" content="1200">' . "\n";
		echo '<meta property="og:image:height" content="630">' . "\n";
		echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
	}

	foreach ( array( 'yandex' => 'yandex-verification', 'google' => 'google-site-verification' ) as $key => $name ) {
		$value = (string) get_option( 'designstack_verification_' . $key, '' );

		if ( '' !== $value ) {
			printf( '<meta name="%1$s" content="%2$s">' . "\n", esc_attr( $name ), esc_attr( $value ) );
		}
	}
}
add_action( 'wp_head', 'designstack_core_head_meta', 3 );

/**
 * Заголовок для OG: тот же, что в <title>, но без хвоста с брендом.
 *
 * @return string
 */
function designstack_core_og_title(): string {
	if ( is_front_page() ) {
		return (string) get_bloginfo( 'name' );
	}

	if ( is_singular( 'resource' ) ) {
		$id      = get_queried_object_id();
		$verdict = (string) designstack_core_get_field( $id, 'verdict' );

		return $verdict ? get_the_title( $id ) . ' — ' . $verdict : get_the_title( $id );
	}

	if ( is_singular() || is_page() ) {
		return (string) get_the_title();
	}

	if ( is_post_type_archive( 'lesson' ) ) {
		return designstack_core_lessons_title();
	}

	$title = designstack_core_archive_title();

	return '' !== $title ? $title : (string) get_bloginfo( 'name' );
}

/**
 * Адрес текущей страницы: canonical, если он есть, иначе запрошенный адрес.
 *
 * @return string
 */
function designstack_core_current_url(): string {
	if ( is_singular() ) {
		$link = get_permalink();

		if ( $link ) {
			return (string) $link;
		}
	}

	if ( is_post_type_archive( 'lesson' ) ) {
		return (string) get_post_type_archive_link( 'lesson' );
	}

	$term = designstack_core_archive_term();

	if ( $term ) {
		return designstack_core_archive_base();
	}

	return home_url( '/' );
}

/**
 * Заголовок страницы уроков: H1, вкладка, превью и крошки.
 *
 * @return string
 */
function designstack_core_lessons_title(): string {
	return __( 'Уроки для UX/UI-дизайнера', 'designstack-core' );
}

/**
 * Число уроков словами: «54 урока».
 *
 * @param int $number Число.
 * @return string
 */
function designstack_core_lessons_count_line( int $number ): string {
	return sprintf(
		'%1$d %2$s',
		$number,
		designstack_core_plural( $number, array( __( 'урок', 'designstack-core' ), __( 'урока', 'designstack-core' ), __( 'уроков', 'designstack-core' ) ) )
	);
}

/**
 * Вводная строка страницы уроков — она же описание для поиска.
 *
 * @return string
 */
function designstack_core_lessons_lead(): string {
	$index   = designstack_core_lessons_index();
	$lessons = 0;

	foreach ( $index as $steps ) {
		$lessons += count( $steps );
	}

	$skills = count( $index );

	return sprintf(
		/* translators: 1: «54 бесплатных урока», 2: «18 навыкам». */
		__( '%1$s по %2$s. У каждого навыка три ступени — Junior, Middle и Senior; в каждом уроке тренажёры, задание и чек-лист.', 'designstack-core' ),
		$lessons . ' ' . designstack_core_plural( $lessons, array( __( 'бесплатный урок', 'designstack-core' ), __( 'бесплатных урока', 'designstack-core' ), __( 'бесплатных уроков', 'designstack-core' ) ) ),
		$skills . ' ' . designstack_core_plural( $skills, array( __( 'навыку', 'designstack-core' ), __( 'навыкам', 'designstack-core' ), __( 'навыкам', 'designstack-core' ) ) )
	);
}

/**
 * Картинка превью: одна на тип страницы.
 *
 * Логотипы вендоров в OG не ставим (brief A9): это чужие товарные знаки,
 * а карточка выглядела бы как реклама сервиса, а не как наша страница.
 *
 * @return string
 */
function designstack_core_og_image(): string {
	// У статьи есть своя обложка 1200×630 — она и идёт в превью ссылки. У ресурса изображение
	// записи это логотип вендора 128×128: и мелко для превью, и чужой знак в нашей карточке.
	if ( is_singular( 'post' ) && has_post_thumbnail( get_queried_object_id() ) ) {
		$cover = get_the_post_thumbnail_url( get_queried_object_id(), 'full' );

		if ( $cover ) {
			return $cover;
		}
	}

	$name = 'default';

	if ( is_singular( 'resource' ) ) {
		$type = designstack_core_get_type( get_queried_object_id() );
		$name = $type ? $type : 'default';
	} elseif ( is_singular( 'post' ) ) {
		$cats = wp_get_post_categories( get_queried_object_id(), array( 'fields' => 'slugs' ) );
		$name = in_array( 'digest', (array) $cats, true ) ? 'digest' : 'collection';
	} else {
		$term = designstack_core_archive_term();

		if ( $term && 'resource_type' === $term->taxonomy ) {
			$name = $term->slug;
		}
	}

	$dir  = get_stylesheet_directory() . '/assets/og/' . $name . '.png';
	$name = file_exists( $dir ) ? $name : 'default';
	$file = get_stylesheet_directory() . '/assets/og/' . $name . '.png';

	return file_exists( $file ) ? get_stylesheet_directory_uri() . '/assets/og/' . $name . '.png' : '';
}

/**
 * Заголовок вкладки: единый хвост с брендом на всех страницах.
 *
 * @param array<string, string> $parts Части заголовка.
 * @return array<string, string>
 */
function designstack_core_title_parts( array $parts ): array {
	if ( is_singular( 'resource' ) ) {
		$id      = get_queried_object_id();
		$verdict = (string) designstack_core_get_field( $id, 'verdict' );

		// Вердикт в заголовке выдачи работает как подзаголовок: по нему видно,
		// что за ресурс, ещё до перехода. Длину держим в пределах 60 знаков с брендом.
		if ( $verdict && mb_strlen( get_the_title( $id ) . $verdict ) < 52 ) {
			$parts['title'] = get_the_title( $id ) . ' — ' . $verdict;
		}
	}

	// У урока заголовок страницы длинный и читается как фраза: в выдаче он обрежется
	// на середине. Во вкладку и в выдачу ставим короткую форму запроса из поля урока —
	// «Как писать тексты ошибок и пустых экранов — урок Junior» (D197), а без поля —
	// «навык · ступень». Длинный заголовок остаётся на самой странице.
	// Проверка — `npx html-validate`, правило long-title, и `check_lessons.py`, строка «заголовок вкладки».
	if ( is_singular( 'lesson' ) ) {
		$id    = get_queried_object_id();
		$step  = designstack_core_step_label( (string) get_post_meta( $id, 'lesson_step', true ) );
		$short = trim( (string) get_post_meta( $id, 'lesson_seo_title', true ) );

		if ( $step && '' !== $short ) {
			/* translators: 1: короткий заголовок урока, 2: ступень. */
			$parts['title'] = sprintf( __( '%1$s — урок %2$s', 'designstack-core' ), $short, $step );
		} elseif ( '' !== designstack_core_lesson_label( $id ) ) {
			$parts['title'] = designstack_core_lesson_label( $id );
		}
	}

	if ( is_post_type_archive( 'lesson' ) ) {
		$parts['title'] = designstack_core_lessons_title();
	}

	$what = designstack_core_single_filter_label();

	if ( '' !== $what ) {
		$parts['title'] = designstack_core_archive_title() . ': ' . $what;
	}

	return $parts;
}
add_filter( 'document_title_parts', 'designstack_core_title_parts', 20 );

/**
 * Разделитель в заголовке вкладки — само тире, а не код.
 *
 * По умолчанию ядро ставит дефис, а русская локаль в `wptexturize()` превращает его в `&#8212;`:
 * на экране то же тире, но в разметке семь знаков вместо одного, и проверка длины заголовка
 * (`html-validate`, правило long-title, 70 знаков) считает заголовок урока длиннее, чем его видит
 * поиск (D197). Само тире `wptexturize()` не трогает.
 *
 * @return string
 */
function designstack_core_title_separator(): string {
	return '—';
}
add_filter( 'document_title_separator', 'designstack_core_title_separator' );

/**
 * robots.txt: закрываем служебное и убираем метки из индекса Яндекса.
 *
 * @param string $output Текст.
 * @param string $public Значение blog_public.
 * @return string
 */
function designstack_core_robots_txt( $output, $public ): string {
	if ( '1' !== (string) $public ) {
		return $output;
	}

	$lines = array(
		'Disallow: /search/',
		'Disallow: /*?s=',
		'Disallow: /styleguide/',
		'Disallow: /suggest/thanks/',
		'Clean-param: utm_source&utm_medium&utm_campaign&utm_content&utm_term&ut_task',
	);

	// Свои директивы ставим до строки Sitemap: формально порядок не важен,
	// но файл читают и люди, а вперемешку он читается как склейка двух файлов.
	$rules = implode( "\n", $lines );

	if ( false !== strpos( $output, 'Sitemap:' ) ) {
		return (string) preg_replace( '/^Sitemap:/m', $rules . "\n\n" . 'Sitemap:', $output, 1 );
	}

	return trim( $output ) . "\n" . $rules . "\n";
}
add_filter( 'robots_txt', 'designstack_core_robots_txt', 10, 2 );

/**
 * Витрина, благодарность и страницы с метками из индекса не нужны.
 *
 * @param array<string, mixed> $robots Правила.
 * @return array<string, mixed>
 */
function designstack_core_robots_service( array $robots ): array {
	if ( is_page( array( 'styleguide', 'thanks' ) ) ) {
		$robots['noindex']  = true;
		$robots['nofollow'] = is_page( 'styleguide' );
	}

	return $robots;
}
add_filter( 'wp_robots', 'designstack_core_robots_service' );

/**
 * Витрина и благодарность не попадают в карту сайта.
 *
 * @param array<string, mixed> $args  Аргументы запроса.
 * @param string               $type  Тип объекта.
 * @return array<string, mixed>
 */
function designstack_core_sitemap_exclude( array $args, string $type ): array {
	if ( 'page' !== $type ) {
		return $args;
	}

	$skip = array();

	foreach ( array( 'styleguide', 'suggest/thanks' ) as $slug ) {
		$page = get_page_by_path( $slug );

		if ( $page ) {
			$skip[] = $page->ID;
		}
	}

	if ( $skip ) {
		$args['post__not_in'] = array_merge( (array) ( $args['post__not_in'] ?? array() ), $skip );
	}

	return $args;
}
add_filter( 'wp_sitemaps_posts_query_args', 'designstack_core_sitemap_exclude', 10, 2 );

/**
 * Карта авторов каталогу не нужна: автор один и своей страницы у него нет.
 *
 * @param mixed  $provider Поставщик карты сайта.
 * @param string $name     Имя поставщика.
 * @return mixed Ложь, если поставщик не нужен.
 */
function designstack_core_sitemap_provider( $provider, string $name ) {
	return 'users' === $name ? false : $provider;
}
add_filter( 'wp_sitemaps_add_provider', 'designstack_core_sitemap_provider', 10, 2 );

/**
 * Страница уроков в карте сайта: архивы типов записей ядро туда не кладёт, а это
 * единственная страница со ссылками на все уроки (D197). Свой поставщик — `wp-sitemap-hubs-1.xml`.
 *
 * @return void
 */
function designstack_core_sitemap_hubs(): void {
	if ( ! class_exists( 'WP_Sitemaps_Provider' ) || class_exists( 'DesignStack_Core_Sitemap_Hubs' ) ) {
		return;
	}

	// phpcs:disable Generic.Files.OneObjectStructurePerFile.MultipleFound
	/**
	 * Разделы сайта, у которых нет своей записи: пока это страница уроков.
	 */
	class DesignStack_Core_Sitemap_Hubs extends WP_Sitemaps_Provider {
		/**
		 * Имя поставщика.
		 */
		public function __construct() {
			$this->name        = 'hubs';
			$this->object_type = 'hubs';
		}

		/**
		 * Адреса.
		 *
		 * @param int    $page_num       Номер страницы карты.
		 * @param string $object_subtype Подтип (не используется).
		 * @return array<int, array<string, string>>
		 */
		public function get_url_list( $page_num, $object_subtype = '' ) {
			$link = get_post_type_archive_link( 'lesson' );

			return 1 === (int) $page_num && $link ? array( array( 'loc' => (string) $link ) ) : array();
		}

		/**
		 * Число страниц карты.
		 *
		 * @param string $object_subtype Подтип (не используется).
		 * @return int
		 */
		public function get_max_num_pages( $object_subtype = '' ) {
			return 1;
		}
	}
	// phpcs:enable

	wp_register_sitemap_provider( 'hubs', new DesignStack_Core_Sitemap_Hubs() );
}
add_action( 'init', 'designstack_core_sitemap_hubs', 20 );

/**
 * Успешная отправка формы: маркер на странице благодарности.
 *
 * Ловить submit самой формы нельзя — она может вернуться с ошибками,
 * и цель засчиталась бы за неудачу. Благодарность открывается только после
 * удачной отправки, поэтому она и есть успех.
 *
 * @param string $content Содержимое.
 * @return string
 */
function designstack_core_thanks_goal( string $content ): string {
	if ( ! is_page( 'thanks' ) || ! in_the_loop() || ! is_main_query() ) {
		return $content;
	}

	return $content . '<span hidden data-track-on-load="suggest_submit"></span>';
}
add_filter( 'the_content', 'designstack_core_thanks_goal' );

/*
 * Ссылки в <head>, которые ведут в никуда. WordPress сам объявляет ленты разделов и таксономий
 * (`/tools/feed/`, `/collections/feed/`), но адреса разделов у нас свои, и лент у них нет: робот
 * Яндекса шёл по объявленной ссылке и получал 404. RSD указывает на xmlrpc.php, который хостинг
 * не обслуживает (405). Основная лента `/feed/` и лента комментариев остаются — они отвечают 200.
 */
remove_action( 'wp_head', 'feed_links_extra', 3 );
remove_action( 'wp_head', 'rsd_link' );

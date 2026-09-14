<?php
/**
 * Разметка блока «Панель фильтров».
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- разметка собрана с экранированием.
echo designstack_core_render_filters( (string) ( $attributes['variant'] ?? 'sidebar' ) );

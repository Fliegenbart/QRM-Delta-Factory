/**
 * Motion Components
 *
 * Reusable animation primitives using Framer Motion.
 * Designed for micro-interactions and delightful UX.
 */

"use client";

import { motion, AnimatePresence, type Variants } from "framer-motion";
import { type ReactNode, type ComponentProps } from "react";

// ============================================================================
// ANIMATION VARIANTS
// ============================================================================

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const fadeInUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
};

export const fadeInDown: Variants = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 10 },
};

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

export const slideInRight: Variants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

export const slideInLeft: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

// Stagger children animation
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
};

// Pulse animation for loading states
export const pulse: Variants = {
  initial: { opacity: 0.5 },
  animate: {
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// ============================================================================
// MOTION COMPONENTS
// ============================================================================

interface MotionDivProps extends ComponentProps<typeof motion.div> {
  children: ReactNode;
}

/**
 * Fade in on mount
 */
export function FadeIn({ children, ...props }: MotionDivProps) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={fadeIn}
      transition={{ duration: 0.2 }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Fade in from below
 */
export function FadeInUp({ children, ...props }: MotionDivProps) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={fadeInUp}
      transition={{ duration: 0.3, ease: "easeOut" }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Scale in (good for modals, cards)
 */
export function ScaleIn({ children, ...props }: MotionDivProps) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={scaleIn}
      transition={{ duration: 0.2, ease: "easeOut" }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Stagger children animations
 */
export function StaggerContainer({ children, ...props }: MotionDivProps) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={staggerContainer}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, ...props }: MotionDivProps) {
  return (
    <motion.div variants={staggerItem} {...props}>
      {children}
    </motion.div>
  );
}

/**
 * Skeleton loader with pulse animation
 */
export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <motion.div
      className={`bg-slate-200 dark:bg-slate-700 rounded ${className}`}
      variants={pulse}
      initial="initial"
      animate="animate"
    />
  );
}

/**
 * Animated presence wrapper for conditional rendering
 */
export function AnimatedPresence({ children }: { children: ReactNode }) {
  return <AnimatePresence mode="wait">{children}</AnimatePresence>;
}

// ============================================================================
// BUTTON ANIMATIONS
// ============================================================================

interface AnimatedButtonProps extends ComponentProps<typeof motion.button> {
  children: ReactNode;
}

/**
 * Button with scale feedback
 */
export function AnimatedButton({ children, className = "", ...props }: AnimatedButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.1 }}
      className={className}
      {...props}
    >
      {children}
    </motion.button>
  );
}

// ============================================================================
// CARD ANIMATIONS
// ============================================================================

/**
 * Card with hover lift effect
 */
export function AnimatedCard({ children, className = "", ...props }: MotionDivProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{
        y: -4,
        boxShadow: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)"
      }}
      transition={{ duration: 0.2 }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}

// ============================================================================
// NUMBER ANIMATIONS
// ============================================================================

interface AnimatedNumberProps {
  value: number;
  className?: string;
  duration?: number;
}

/**
 * Animated number counter
 */
export function AnimatedNumber({ value, className = "", duration = 0.5 }: AnimatedNumberProps) {
  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration }}
      className={className}
    >
      {value}
    </motion.span>
  );
}

// ============================================================================
// PROGRESS ANIMATIONS
// ============================================================================

interface AnimatedProgressProps {
  value: number;
  max?: number;
  className?: string;
  barClassName?: string;
}

/**
 * Animated progress bar
 */
export function AnimatedProgress({ value, max = 100, className = "", barClassName = "" }: AnimatedProgressProps) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className={`h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden ${className}`}>
      <motion.div
        className={`h-full bg-[var(--brand)] rounded-full ${barClassName}`}
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      />
    </div>
  );
}

// ============================================================================
// FLOW / TIMELINE ANIMATIONS
// ============================================================================

interface FlowStepProps {
  isActive?: boolean;
  isComplete?: boolean;
  children: ReactNode;
  className?: string;
}

/**
 * Animated flow step indicator
 */
export function FlowStep({ isActive, isComplete, children, className = "" }: FlowStepProps) {
  return (
    <motion.div
      initial={{ opacity: 0.5, scale: 0.95 }}
      animate={{
        opacity: isActive || isComplete ? 1 : 0.5,
        scale: isActive ? 1.05 : 1,
      }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Animated connector line between flow steps
 */
export function FlowConnector({ isActive }: { isActive?: boolean }) {
  return (
    <div className="flex-1 h-0.5 bg-slate-200 dark:bg-slate-700 mx-2 overflow-hidden">
      <motion.div
        className="h-full bg-[var(--brand)]"
        initial={{ width: 0 }}
        animate={{ width: isActive ? "100%" : 0 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      />
    </div>
  );
}

// Re-export framer-motion for convenience
export { motion, AnimatePresence };
